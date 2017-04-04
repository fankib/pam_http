import string
import time
import os
import os.path
import json
from flask import Flask
from Crypto.Hash import SHA256
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from subprocess import call


file_config = 'lockid.config'
file_challenge = '/tmp/challenge'
file_http_success = '/tmp/http_success'
#default_user_hash = 'f75778f7425be4db0369d09af37a6c2b9a83dea0e53e7bd57412e4b060e607f7' #supersecret

# "y": "9839048587665537347297745996269176812347054340950860355708728554724422654849820719409837751410449321901874938902871277154007809942591059332748396381758115465270630137111827444085024440498044069714771765587941527278557111758785627864517360378547706636839802409479632295716658745940589716786835705458922433721083857751924815759522324615086325061398847694985947587486896546017366133071039186344777945373266475786555472349588683057994524554925332969798187117071712577767338634538416900913002956494870324616054272922933392549268454459111023144018712492525432429782647875877635354516695029498349860832419090117549583833275",

# init config:
configPath = os.path.dirname(os.path.abspath(__file__)) + '/' + file_config;
configJson = open(configPath, 'r')
config = json.load(configJson)
max_challenge_age = int(config['max_challenge_age'])
user_name = config['user_name']
command_unlock = config['command_unlock'].split()
command_lock = config['command_lock'].split()
generator = int(config['g'])
modulus = int(config['p'])
publicKey = int(config['y'])

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
	
	
def validToken(t, s):
	key = ElGamal.construct([modulus, generator, publicKey])
	challenge = readChallenge()
	h = SHA256.new(challenge).digest()
	if(key.verify(h, [int(t),int(s)])):
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

@app.route('/unlock/<t>/<s>')
def unlock(t, s):
	if ( not validChallenge()):
		return 'challenge too old\n';
	if ( validToken(t, s) ):
		grantAccess()
		unlockScreen()
		return 'ok\n';
	return 'notok\n';
	
@app.route('/lock/<t>/<s>')
def lock(t, s):
	if ( not validChallenge() ):
		return 'challenge too old \n'
	if ( validToken(t, s) ):
		lockScreen();
		return 'locked\n'
	return 'notok\n'

if __name__ == '__main__':
	initFile(file_challenge)
	initFile(file_http_success)
	generateChallenge()
	app.run(debug=False, host='0.0.0.0')
