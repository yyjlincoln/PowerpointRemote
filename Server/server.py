import logger
import pack
from dbconnect import keycollection, session
import threading
import socket
import time
import secrets
import base64
from Crypto.Cipher import AES
import mongoengine
import json

server = ('0.0.0.0', 8085)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(server)
s.listen(10)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

deadConnection = []


def connection_handler():
    # connection handler
    global s

    while True:
        sx, addr = s.accept()

        thd = threading.Thread(target=connection_keep_recv, args=(sx, addr))
        thd.setDaemon(True)
        thd.start()


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


def parseData(sx, addr, data):
    opcode, ts, identity, verif, encrypted, actdata = pack.unpack(data)
    if encrypted:
        query = session.query(identity=identity).first()
        if query:
            opcode, ts, identity, verif, encrypted, actdata = pack.unpack(data, key=query.key)

    operation=None
    for op, code in pack.opcode_mapping.items():
        if code==opcode:
            operation=op
    
    if operation=='register':
        _key=secrets.token_hex(32).encode()
        key = base64.b64encode(_key).decode()
        keycollection(rand=json.loads(actdata)['rand'], key=_key).save()
        connection_send(sx,addr,pack.pack_json('success',{
            'message':'Identity created'
        }, encrypted=True, key=_key))



    #     connection_send(sx, addr, pack.pack('success',{
    #         'operation': 'register',
    #         'identity':identity
    #     }))
    #     token = secrets.token_urlsafe(32)
    #     session(identity = identity, token=token, key=key)
    #     return

    # print(opcode, ts, identity, token, actdata, identity)

def init():
    mongoengine.connect('premote')
    connection_handler()

init()