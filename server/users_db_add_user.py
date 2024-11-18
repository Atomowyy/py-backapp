#!/usr/bin/env python3

import json
import hashlib
import os
import sys
from base64 import b64encode

if sys.platform == 'win32':
    import msvcrt
else:
    import termios


def get_passwd_unix(prompt: str) -> str:
    print(prompt)

    fd = sys.stdin.fileno()  # get file descriptor associated with file-like object (stdin, stdout, stderr)
    old_settings = termios.tcgetattr(fd)  # Get current terminal settings

    # terminal settings - canonical mode, disable echo, keep interrupts
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

        passwd = ''
        ch = sys.stdin.read(1)  # Read one byte

        while ch != '\n':
            passwd += ch
            ch = sys.stdin.read(1)
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return passwd


def get_passwd_windows(prompt: str) -> str:
    print(prompt)

    ch = msvcrt.getch()
    if ch == b'\x03':  # ctrl + c
        print('Exiting...')
        exit()

    passwd = ''
    while ch != b'\r':
        passwd += ch.decode(errors='replace')
        ch = msvcrt.getch()

    return passwd


users = json.load(open(os.path.join(os.path.dirname(__file__), 'users_db.json'), 'r'))

username = input('Username: ')
if username in users:
    print('Username already exists')
    exit()

password = get_passwd_windows('Password: ') if sys.platform == 'win32' else get_passwd_unix('Password: ')
retyped_password = (
    get_passwd_windows('Retype Password: ')) if sys.platform == 'win32' else get_passwd_unix('Retype Password: ')

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
with open(os.path.join(os.path.dirname(__file__), 'users_db.json'), 'w') as user_db:
    user_db.write(json.dumps(users, indent='\t'))

print('\nUser added successfully')
