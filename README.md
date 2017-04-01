# pam_http
Unlock or Lock your linux system over a HTTP Channel. With a smartphone for example.

# How it looks like
Type your (locki-)password into your smartphone. With the button 'unlock' you authenticate your predefined user account in the pam-ecosystem. 
This allows you to unlock the greeter or screensaver with your smartphone. Or even sudo can be unlocked like this.
A token is only valid once and expires after 10 seconds. This allows you to detect malicious behaviour.

# one-user-world
Due to the special security layout, there is only one user supported. Imagine a 2-user-world: there exists a smartphone A and a smartphone B allowed to unlock a certain machine for account A and account B.
The machine recognizes if the smartphone A or B sent a valid token. But in the moment when the physical user presses the login button, the machine can not determinate if the user A or user B sits in front of him.
(Maybe it is possible with more assumptions in the future.
But its not on my priority list).

# Security
It is assumed, that the adversery has no control over the user account to authenticate, root and the used http-client (aka smartphone).
Under this assumptions the goal is that:
 * no other party can learn something over the shared secret
 * no other party can use captured data without beeing noticed.
 * no other party can not "dos" the system with caputred data.

## compromised user account
This can be prevented with correct pam configuration. Do not allow this authentication method for switching user services.
The used files to exchange inter process data are only visible to the user and root.

## attack over the communication
There is no way to prevent malicious behaviour on the network level.
But this is no problem, because the traffic does not reveal any secrets.
Captured, valid tokens expires after their first use or 10 seconds.
Or when the next valid token is received.

## detect malicious behaviour
When there still is a way to break in the system, the token should expire. 
So when a token is marked as ok on the smartphone but pam asks for a password, you should be super suspicious,
reinstall the software and change the secrets.

# How it works
There exists 3 parts:
 * the pam module pam_http.so, used to integrate the lockid into pam
 * the lockid service: a python webserver used for the communication
 * the locki app: a python script for linux or with buildozer on android. For the user to interact with the system.

## pam_http.so
Its a really easy module: it reads the content from /tmp/http_success and when there is an entry, no older than 10 seconds it pam-authenticates it.
After a successfull authentication the file is cleared.

## lockid - webservice
The daemon creates a challenge and provides it under 0.0.0.0:5000/challenge. A client is authenticated when he can solve the challenge in this way:
token = hash(challenge || hash(secret)). To avoid replay attacks: a challenge is only available for 3 seconds and only valid once.
The deamon does not need to know the secret in plaintext. It can be substituated with hash_secret = hash(secret). 

## locki - the app
This is a simple implementation of a client. It provides a form for the server to connect and the secret to input.

# Installation 
Install all the dependencies for python or buildozer first (or when it fails)..

## pam_http:
run the script `$ ./pam/build`

## lockid:
run `$ python ./lockid/server.py`
or use the template under ./systemd/lockid.service to create a systemd service (instructions in the file)

## locki:
run `$ python ./locki/main.py`
or build with buildozer an android app: `buildozer android release deploy run`




