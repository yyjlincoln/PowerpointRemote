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
            except:
                logger.handled_exception(
                    'Unable to parse data, dropped...', address=addr)
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
    opcode, ts, identity, token, jsondata = pack.unpack(data)

    if time.time()-ts < 0:
        connection_send(sx, addr, pack.pack('warning', {
            'message': 'Check clock',
            'type': '1'
        }))
    
    operation=None
    for op, code in pack.opcode_mapping.items():
        if code==opcode:
            operation=op
    
    if operation=='register':
        key = base64.b64encode(secrets.token_hex(32).encode()).decode()
        keycollection(rand=jsondata['rand'], key=key).save()
        connection_send(sx, addr, pack.pack('success',{
            operation: 'register'
        }))
        token = secrets.token_urlsafe(32)
        session(identity = identity, token=token, key=key)
        # AES.new(base64.b64decode(key),AES.MODE_CFB).encrypt_and_digest()
        # connection_send(sx,addr,)
        return

    print(opcode, ts, identity, token, jsondata, identity)

def init():
    mongoengine.connect('premote')
    connection_handler()

init()