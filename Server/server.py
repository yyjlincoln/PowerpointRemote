import logger
import pack
from dbconnect import keycollection, session
import threading
import socket
import time

server = ('0.0.0.0', 8085)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(server)
s.listen(10)

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

    print(opcode, ts, identity, token, jsondata, identity)
