import struct
import json
import time
import hashlib
import base64
from Crypto.Cipher import AES
import logger

'''
Data structure:

Operation Code [I] + Timestamp [d] + Client Identity [32s] + hash_verif (first 12 of hash) [12s] + encrypt [?] + actdata [?s]
'''

version = 'init.1'

opcode_mapping = {
    'register':0x0000,
    'heartbeat':0x0001,
    'next':0x0002,
    'previous':0x0003,
    'success':0xF000,
    'failed':0xF001,
    'warning':0xF002,
    'general':0xF003,
    'tokenexchange':0xF004,
    'loggedin':0xF009
}

class PackException(Exception):
    'Error occured when packing or unpacking the data.'

Identity = ''

def set_identity(identity):
    global Identity
    Identity = identity

def calc_verif(data, identity = Identity):
    _identity = struct.pack('32s', Identity.encode('utf-8'))
    return hashlib.md5(_identity[0:32]+data).digest()[0:12]

def encrypt(raw, key):
    iv = struct.pack(f'{AES.block_size}s',calc_verif(raw)) # Make the length of the iv to be equal to the block_size
    cip = AES.new(key, mode=AES.MODE_CFB, iv=iv).encrypt(raw)
    return cip

def decrypt(raw, key, iv):
    iv = struct.pack(f'{AES.block_size}s',iv) # Make the length of the iv to be equal to the block_size    
    cip = AES.new(key, mode=AES.MODE_CFB, iv=iv).decrypt(raw)
    return cip

def pack(operation, raw, encrypted=False, key=None):
    if operation not in opcode_mapping:
        raise PackException(f'Operation {str(operation)} can not be mapped to any existing operation code.')

    verif = calc_verif(raw)
    data = raw

    if encrypted and not key:
        raise PackException('No key is provided.')
    elif encrypted and key:
        data = encrypt(raw, key)

    return struct.pack(f'Id32s12s?{len(data)}s',opcode_mapping[operation], float(time.time()), Identity.encode('utf-8'), verif, encrypted, data)

def unpack(raw, key=None):
    # Calculate package size
    _s = struct.calcsize('Id32s12s?')
    # Calculate actdata size
    data_length = len(raw)-_s
    if data_length<0:
        raise PackException('Datalength must not be less than 0. Some data is missing.')
    # Unpack
    opcode, ts, identity, verif, encrypted, actdata = struct.unpack(f'id32s12s?{data_length}s', raw)

    # Try to decrypt, if needed
    if encrypted and key:
        try:
            actdata = decrypt(actdata, key, verif)
            val = calc_verif(actdata, identity=identity)
            print(val, verif)
        except:
            logger.warn('The data can not be decrypted using the key provided. Returning raw data.')
    elif encrypted and not key:
        logger.warn('The data is declated to be encrypted but no key is provided. Returning raw data.')

    return opcode, ts, identity.decode(), verif, encrypted, actdata

def pack_json(operation, obj, encrypted=False, key=None):
    return pack(operation, json.dumps(obj).encode('utf-8'), encrypted, key)

def unpack_json(raw, key=None):
    opcode, ts, identity, verif, encrypted, actdata = unpack(raw, key)
    try:
        actdata=json.loads(actdata.decode('utf-8'))
    except:
        actdata=None
    return opcode, ts, identity, verif, encrypted, actdata