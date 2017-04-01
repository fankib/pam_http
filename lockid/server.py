import random
import string
import time
import os.path
from flask import Flask
from Crypto.Hash import SHA256
from subprocess import call

max_challenge_age = 3
file_challenge = '/tmp/challenge'
file_http_success = '/tmp/http_success'
secret_user_hash = 'f75778f7425be4db0369d09af37a6c2b9a83dea0e53e7bd57412e4b060e607f7' #supersecret
user_name = 'beni'
command_unlock = ['/usr/bin/xscreensaver-command', '-deactivate'];
command_lock = ['/usr/bin/xscreensaver-command', '-lock']

# make 600 files:

app = Flask(__name__)

def initFile(file_name):
	call(['/usr/bin/touch', file_name])
	call(['/usr/bin/chmod', '600', file_name])

def randomword(length):
   return ''.join(random.choice(string.ascii_letters) for i in range(length))

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
	challenge = readChallenge()
	h = SHA256.new()
	h.update(challenge)
	h.update(secret_user_hash.encode('ASCII'))
	result = h.hexdigest()
	if(token == result):
		generateChallenge()
		return True
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
	if ( not validChallenge()):
		generateChallenge()
	return readChallenge()

@app.route('/unlock/<token>')
def unlock(token):
	if ( not validChallenge()):
		return 'challenge too old\n';
	if ( validToken(token) ):
		grantAccess()
		unlockScreen()
		return 'ok\n';
	return 'notok\n';
	
@app.route('/lock/<token>')
def lock(token):
	if ( not validChallenge() ):
		return 'challenge too old \n'
	if ( validToken(token) ):
		lockScreen();
		return 'locked\n'
	return 'notok\n'

if __name__ == '__main__':
	initFile(file_challenge)
	initFile(file_http_success)
	generateChallenge()
	app.run(debug=False, host='0.0.0.0')
