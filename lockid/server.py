import string
import time
import os
import os.path
import json
import hashlib
import base64
from Crypto.Random import random
from flask import Flask
from subprocess import call
from ecdsa import VerifyingKey, NIST256p, BadSignatureError

file_config = 'lockid.config'
file_challenge = '/tmp/challenge'
file_http_success = '/tmp/http_success'

# init config:
configPath = os.path.dirname(os.path.abspath(__file__)) + '/' + file_config;
configJson = open(configPath, 'r')
config = json.load(configJson)
max_challenge_age = int(config['max_challenge_age'])
user_name = config['user_name']
command_unlock = config['command_unlock'].split()
command_lock = config['command_lock'].split()
public_key = VerifyingKey.from_string(base64.b64decode(config['y']), curve=NIST256p, hashfunc=hashlib.sha256)

print(configPath)

app = Flask(__name__)

def initFile(file_name):
	call(['/usr/bin/touch', file_name])
	call(['/usr/bin/chmod', '600', file_name])

def randomword(length):
   return ''.join(random.StrongRandom().choice(string.ascii_letters) for i in range(length))

def generateChallenge():
	challenge = randomword(23) #128-bit security
	writeChallenge(challenge)

def readChallenge():
	f = open(file_challenge, 'r')
	return (f.read(23)).encode('ASCII')
	
def writeChallenge(challenge):
	f = open(file_challenge, 'w')
	f.write(challenge);
	f.close()
	
def validChallenge():
	now = int(time.time())
	then = int(os.path.getmtime(file_challenge))
	age = now - then
	print("age of challenge: {}".format(age))
	return age < max_challenge_age
	
	
def validToken(token):
	signature = base64.urlsafe_b64decode(token)	
	challenge = readChallenge()
	try:
		public_key.verify(signature, challenge)
		generateChallenge()
		return True
	except BadSignatureError as b :
		print('bad signature')		
	return False
	
def grantAccess():
	timestamp = int(time.time())
	f = open(file_http_success, 'w')
	f.write(user_name)
	f.write(';')
	f.write('{}'.format(timestamp))
	f.write('\n')
	
def unlockScreen():
	call(command_unlock)

def lockScreen():
	call(command_lock)
	
@app.route('/')
def index():
	return 'Hello. This is for clients only. Use your secret to solve /challenge.'

@app.route('/challenge')
def challenge():
	if ( not validChallenge() ):
		generateChallenge()
	return readChallenge()

@app.route('/unlock/<t>')
def unlock(t):
	if ( not validChallenge()):
		return 'challenge too old\n';
	if ( validToken(t) ):
		grantAccess()
		unlockScreen()
		return 'ok\n';
	return 'notok\n';
	
@app.route('/lock/<t>')
def lock(t):
	if ( not validChallenge() ):
		return 'challenge too old \n'
	if ( validToken(t) ):
		lockScreen();
		return 'locked\n'
	return 'notok\n'

if __name__ == '__main__':
	initFile(file_challenge)
	initFile(file_http_success)
	generateChallenge()
	app.run(debug=False, host='0.0.0.0')
