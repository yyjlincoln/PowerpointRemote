import struct
import json
import time
import hashlib
import base64

'''
Data structure:

Operation Code [I] + Timestamp [d] + Client Identity [32s] + Token [32s] + hash_verif (first 12 of hash) [12s] + jsondata [?s]
'''

version = 'init.0'

opcode_mapping = {
    'register':0x00000000,
    'heartbeat':0x00000001,
    'next':0x00000002,
    'previous':0x00000003,
    'success':0x00010000,
    'failed':0x00010001,
    'warning':0x00010002
}

class PackException(Exception):
    'Error occured when packing or unpacking the data.'

Identity = ''
Token = ''

def set_token(token):
    global Token
    Token = token

def set_identity(identity):
    global Identity
    Identity = identity

def pack(operation, data):
    if operation not in opcode_mapping:
        raise PackException(f'Operation {str(operation)} can not be mapped to any existing operation code.')
    data = json.dumps(data).encode('utf-8')

    # Calculate MD5 for verification
    _token = struct.pack('32s', Token.encode('utf-8'))
    verif = hashlib.md5(_token[0:32]+data).digest()[0:12]
    return struct.pack(f'Id32s32s12s{len(data)}s',opcode_mapping[operation], float(time.time()), Identity.encode('utf-8'), Token.encode('utf-8'), verif, data)

def unpack(data):
    # Calculate package size
    _s = struct.calcsize('Id32s32s12s')
    # Calculate jsondata size
    data_length = len(data)-_s
    if data_length<0:
        raise PackException('Datalength must not be less than 0. Some data is missing.')
    # Unpack
    opcode, ts, identity, token, verif, jsondata = struct.unpack(f'id32s32s12s{data_length}s', data)
    # Validate data
    val = hashlib.md5(token[0:32]+jsondata).digest()[0:12]
    if val!=verif:
        raise PackException('Data validation failed, dropped.')
    # Undo json
    jsondata=json.loads(jsondata.decode('utf-8'))
    # Format data
    identity = identity.decode('utf-8')
    token = token.decode('utf-8')
    return opcode, ts, identity, token, jsondata

