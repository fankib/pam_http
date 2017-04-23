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
 * no other party can learn something about the secret
 * no other party can use captured data without beeing noticed.

## compromised user account
This can be prevented with correct pam configuration. Do not use this method for `su`-authentication:
if you provide a valid token, every user on the system is allowed to authenticate as you.
That's why we have `sudo`.
In additional: the used files to exchange inter process data are only visible to the user and root.
Note that the config of the lockid-deamon is a possibility to escalate privileges: if the user changes the configured 'username' to 'root'.

## attack on the network level
There is no way to prevent malicious behaviour on the network level.
But this is no problem, because the traffic does not reveal any secrets.
Captured, valid tokens expires after their first use or 10 seconds this prevents a man-in-the-middle to collect valid tokens for a later usage.
Or when the next valid token is received.
Also the challenge expries after 3 seconds to avoid replay attacks.

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
Its a simple module: it reads the content from /tmp/http_success and when there is an entry, no older than 10 seconds it pam-authenticates it.
After a successfull authentication the file is cleared.

## lockid - webservice
The daemon creates a challenge and provides it under 0.0.0.0:5000/challenge. A client is authenticated when he can solve the challenge in this way:
token = sign_sk(challenge). To avoid replay attacks: a challenge is only available for 3 seconds and only valid once.
Due to public-key-crypto the deamon does not need to know the secret in plaintext. 

## locki - the app
This is a implementation of a client. It provides a formular to input the server and the secret.

# Installation 
Install all the dependencies for python or buildozer first (or when it fails)..

at least you need: kivy,plyer,pycrypto,ecdsa (`$ sudo pip install kivy plyer pycrypto ecdsa`).

## pam_http:
run the script `$ ./pam/build`

## lockid:
run `$ python ./lockid/server.py`
or use the template under ./systemd/lockid.service to create a systemd service (instructions in the file)
The configuration is located under `lockid/lockid.config`.

## locki:
run `$ python ./locki/main.py`
or build with buildozer an android app: `[./locki]$ buildozer android debug deploy run`

# Generate new secrets
As it is not recommended to use the default password 'supersecret' in any way, you have to generate a new secret. 

Use the python shell to acomplish this:

```
$ cd ./locki/
$ python
>>> import client
>>> client.createPublicKeyFromSecret(b'<new-secret>')
b'bzi8FV6aDp870moRHeiHOd45ehlYiKAZupaAoPYKcXsJy/igvNN9PgiJCL0aJ9hwJQn7aLMenGNUOg0Fw2lSwQ=='
<ctrl+d>
```

configure the lockid-deamon with the new publickey (the y-attribute)


