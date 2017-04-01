import sys
import json
from Crypto.Hash import SHA256

is_linux = sys.platform == 'linux'
is_android = sys.platform == 'linux4'

server = 'http://localhost:5000'

if is_linux:
	from urllib import request
if is_android:
	import urllib
	
def urlopen(url):
	print('urlopen: ' + url)
	if is_android:
		return urllib.urlopen(url)
	if is_linux:
		return request.urlopen(url)
	return None
	
def createMyDigest(secret):
	h = SHA256.new()
	h.update(secret)
	return h.hexdigest()
	
def readChallenge():
	f = urlopen(server+'/challenge')
	return f.read(23)
	
def sendUnlockToken(token):
	f = urlopen(server+'/unlock/'+token)
	return f.readline().decode('ASCII')

def sendLockToken(token):
	f = urlopen(server+'/lock/'+token)
	return f.readline().decode('ASCII')
	
def createToken(secret):
	challenge = readChallenge()
	mydigest = createMyDigest(secret)
	h = SHA256.new()
	h.update(challenge)
	h.update(mydigest.encode('UTF-8'))
	return h.hexdigest()
	
def unlock(secret):
	return sendUnlockToken(createToken(secret))
	
def lock(secret):
	return sendLockToken(createToken(secret))
	
if __name__ == '__main__':
	print(unlock(b'supersecret'))
	
