from socket import socket, SHUT_RDWR, AF_INET, SOCK_STREAM
import logger
import random
import pack
import requests
from Crypto.Cipher import AES
import secrets

server = ('mcsrv.icu',8085)
keyserver = 'keyserver.premote.mcsrv.icu'
key = ''

def init():
    global key

    logger.info('Initializing...')
    s = socket(AF_INET, SOCK_STREAM)

    logger.log(f'Using pack version {pack.version}')

    logger.info(f'Connecting to the server: {server[0]} on port {str(server[1])}')
    s.connect(server)

    logger.info('Registering existance...')
    rand = secrets.token_urlsafe(32)
    s.send(pack.pack('register',{
        'rand':rand
    }))

    logger.info('Obtaining key for encryption...')
    # Obtain secrect key for encryption, via HTTPS
    r = requests.get('https://'+keyserver+'/obtain', {
        'rand': rand
    })
    if 'key' not in r.json():
        logger.fatal('Failed to obtain key!')
    key = r.json()['key']

    logger.info('Successfully obtained key!')

def encrypt(key):
    AES.new(key, AES.MODE_CFB)


try:
    init()
except Exception as e:
    logger.fatal('An exception occured:',Exception=e)

