import json
import hashlib

users = json.load(open('user_db.json', 'r'))

username = input('Username: ')
if username in users:
    print('Username already exists')
    exit()


def hash_passwd(passwd):
    return hashlib.sha512(passwd.encode()).hexdigest()


password = hash_passwd(input('Password: '))
retyped_password = hash_passwd(input('Retype Password: '))

if password != retyped_password:
    print('Passwords do not match')
    exit()

# add user to the dict
users[username] = password
# dump dict as json into user_db.json
with open('user_db.json', 'w') as user_db:
    user_db.write(json.dumps(users, indent='\t'))

print('\nUser added successfully')
