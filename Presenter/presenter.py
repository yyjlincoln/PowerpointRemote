import socket
import logger
import random
import pack
import requests
import secrets
import json
import threading
import base64


server = ('mcsrv.icu',8085)
keyserver = 'keyserver.premote.mcsrv.icu'
key = ''

deadConnection = []

def connection_keep_recv(sx, addr):
    global deadConnection
    while sx not in deadConnection:
        try:
            data = sx.recv(1024)
            if data == b'':
                terminate_connection(sx, addr)
                logger.log('Exit thread', address=addr)
                break

            try:
                parseData(sx, addr, data)
            except Exception as e:
                logger.handled_exception(
                    'Unable to parse data, dropped...', address=addr, exception =e)
        except socket.error:
            terminate_connection(sx,addr)
        except Exception as e:
            logger.exception(e)


def terminate_connection(sx, addr):
    try:
        if sx in deadConnection:  # Marked as dead by the other thread
            deadConnection.remove(sx)
        else:
            deadConnection.append(sx)  # Mark as dead
        logger.log(
            'Connection reset, disgarding connection...', address=addr)
        sx.shutdown(socket.SHUT_RDWR)
        sx.close()
    except Exception as e:
        logger.hanex(e)


def connection_send(sx, addr, data):
    try:
        sx.send(data)
    except socket.error:
        terminate_connection(sx,addr)
        return
    except:
        raise

def parseData(sx,addr,data):
    opcode, ts, identity, verif, encrypted, actdata = pack.unpack_json(data, key=key)

    operation=None
    for op, code in pack.opcode_mapping.items():
        if code==opcode:
            operation=op
    
    if operation=='loggedin':
        pack.set_identity(identity)
        logger.info(f'Set identity as {identity}')
    logger.info(opcode,ts,identity,verif,encrypted,actdata)

def init():
    global key

    logger.info('Initializing...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    logger.log(f'Using pack version {pack.version}')

    logger.info(f'Connecting to the server: {server[0]} on port {str(server[1])}')
    s.connect(server)

    logger.info('Starting listening thread...')
    t = threading.Thread(target=connection_keep_recv, args=(s, server))
    t.setDaemon(True)
    t.start()

    logger.info('Registering existance...')
    rand = secrets.token_urlsafe(32)
    s.send(pack.pack('register',json.dumps({
        'rand':rand
    }).encode()))
    logger.info('Existance registered, waiting for the reply...')

    logger.info('Obtaining key for encryption...')
    # Obtain secrect key for encryption, via HTTPS
    r = requests.get('https://'+keyserver+'/obtain', {
        'rand': rand
    })
    if 'key' not in r.json():
        logger.fatal('Failed to obtain key!')
    key = base64.b64decode(r.json()['key'])

    logger.info('Successfully obtained key!')

    # while True:
    #     logger.info('Loading...')
    t.join()



try:
    init()
except Exception as e:
    logger.fatal('An exception occured:',Exception=e)

