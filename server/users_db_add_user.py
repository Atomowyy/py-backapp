import json
import hashlib
import os
from base64 import b64encode

users = json.load(open('users_db.json', 'r'))

username = input('Username: ')
if username in users:
    print('Username already exists')
    exit()

password = input('Password: ')
retyped_password = input('Retype Password: ')

if password != retyped_password:
    print('Passwords do not match')
    exit()

# hashing password
salt = b64encode(os.urandom(16)).decode()  # generate random 16 bytes
password_hash = hashlib.scrypt(password=password.encode(), salt=salt.encode(), n=2**12, r=10, p=1, dklen=128)
password_hash_base64 = b64encode(password_hash)

password_dict = {
    "password": password_hash_base64.decode(),
    "salt": salt
}

# add user to the dict
users[username] = password_dict
# dump dict as json into users_db.json
with open('users_db.json', 'w') as user_db:
    user_db.write(json.dumps(users, indent='\t'))

print('\nUser added successfully')
