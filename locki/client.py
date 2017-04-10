import sys
import json
import time
import hashlib
import base64
from Crypto.Protocol import KDF
from ecdsa import SigningKey, NIST256p


is_linux = sys.platform == 'linux'
is_android = sys.platform == 'linux4'

server = 'http://localhost:5000'
generator = 9917414805094635192269004123972663839730378308321699993020469552936378795425881647428015997948778962711500593241874387295553479468087226286117930469790827188487556234424746404509187964366424627411469908177385792848361528017821165773509471818032462888233997026241709783871772919618418651081273591008300413394652448587172367382715553266071916341362774450671068981287028121415309575881269641060092997720147012684337387360482672652698157468482829691818941060842053533997449300215307764688522214460374861784601905887798049780221735036416733051890536398834635289268842863146257665683607077772415189639133100012013899544910
modulus = 18400719931780606010354578153091462964633015184876091368240036452055385384077399544428733433101442361631341566988837268545674028143749405972439006021144422893719466723671986917570830072171801082259227142605005237552561661606188301390914124891181333239143327574025532465581355977844230836416706703256776861964854385586768282258448845846065568103043142986542323786024680229601368682676065333920312423744260262488646206126992474717581279539460828197464556517500326310898847500827583162550722488450775517322558775014262873693909825130738374207846777833680207371838228375145103856193406043402799463632985439297892281117567

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

# BigEndian encoding (unsigned)
# python3: x = int.from_bytes(x_bytes, byteorder='big')
def bytesToInt(x_bytes):
	factor = 1
	x_bytes = bytearray(x_bytes[::-1]) # reverse
	result = 0
	for b in x_bytes:
		result = result + factor*b
		factor = factor*256
	return result	

def serializePublicKey(publicKey):
	str_pubkey = publicKey.to_string()
	return base64.b64encode(str_pubkey)

def createPublicKeyFromSecret(secret):
	x = createSecretKey(secret)
	y = createPublicKey(x)
	return serializePublicKey(y)

def createSecretKey(secret):
	x_bytes = KDF.PBKDF2(secret, b'sjxA9e2$', 32, count=1000)	
	x = bytesToInt(x_bytes)	
	if ( x <= 1 or x >= NIST256p.order ):
		raise Error('secret key out of range')
	return SigningKey.from_secret_exponent(x, curve=NIST256p, hashfunc=hashlib.sha256)

def createPublicKey(secretKey):
	return secretKey.verifying_key;
	
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
	ts_start = time.time()	
	key = createSecretKey(secret)
	ts_createSecret = time.time()		
	challenge = readChallenge()
	ts_challenge = time.time()
	sig = key.sign_deterministic(challenge)
	ts_sig = time.time()
	
	# log timestamps:
	print('createSecret: ', (ts_createSecret - ts_start)*1000)	
	print('read challenge: ', (ts_challenge - ts_createSecret)*1000)	
	print('sig :', (ts_sig - ts_challenge)*1000)
	
	return (base64.urlsafe_b64encode(sig)).decode('ASCII')
	
def unlock(secret):
	return sendUnlockToken(createToken(secret))
	
def lock(secret):
	return sendLockToken(createToken(secret))
	
if __name__ == '__main__':
	secret = 'supersecret'	
	y = createPublicKeyFromSecret(secret)
	print('y', y.decode('ASCII'))
	print(unlock(secret))
	
