from platform import system
from socket import socket, error as socket_error
from time import sleep
from xml.sax import parse
from tcp_client import TcpClient
from datetime import datetime
import os
import sys
import argparse
import json


def user_check(config: json) -> bool:
    username = config['username']
    if username == '':
        return False
    return True


def server_check(config: json) -> bool:
    server: str = config['server']
    print(server)
    if server == '':
        return False
    return True


# def token_check(config, client) -> bool:
#     token: str = config['token']
#     if token == '':
#         server_response = client.get_auth_token()
#         #print(server_response)
#         while server_response == -1:
#             client = TcpClient()
#             #print("Authentication failure")
#             server_response = client.get_auth_token()
#             #print(server_response)
#         print("Authenticated successfully!")
#         #print('Token granted, please restart py-backapp')
#         return True
#     return False


def server_set(config) -> None:
    config['server'] = str(input('Server IP: '))
    config['port'] = str(input('Server port: '))
    with open('config.json', 'w') as cfg:
        cfg.write(json.dumps(config, indent='\t'))
    print('Server settings edited successfully!')


def user_set(config) -> None:
    config['username'] = str(input('Username: '))
    with open('config.json', 'w') as cfg:
        cfg.write(json.dumps(config, indent='\t'))


def print_menu() -> None:
    print('1.Send files to the server')
    print('2.Send whole directories to the server')
    print('3.Download files from the server')
    print('4.Download directories from the server')
    print('5.List your uploaded files')
    print('6.Synchronize data')
    print('7.Delete selected uploaded files')
    print('8.Delete all of your uploaded files')
    print('9.Exit')


def menu() -> None:
    # verifying JSON
    config: json = json.load(open('config.json', 'r'))
    reload_needed = False

    if not server_check(config):
        print('There is no specified server, please enter valid IP address and port number')
        server_set(config)
        reload_needed = True
    if not user_check(config):
        print("There is no user logged in.")
        user_set(config)
        reload_needed = True

    if reload_needed:
        # replace current process with the new instance of itself
        os.execv(sys.executable, [sys.executable] + sys.argv)

    client = TcpClient()
    server_response = client.verify_token()
    if server_response == -1:
        print(server_response)
        while server_response == -1:
            client = TcpClient()
            print("Authentication failure")
            server_response = client.get_auth_token()
            print(server_response)
    print("Authenticated successfully!")

    while True:
        # if token_check(config, client):
        #     print("Connected to the server!")
        print(f'Hello {config["username"]}')

        input()  # press enter to show the menu
        print_menu()

        client = TcpClient()
        client.send_auth_token()

        match input():
            case '1': #dziala - wysyłanie pliku
                print('--------------------------------------------')
                path: str = input('Specify path to the file: ')
                response = client.store(path , f'{config['username']}')
                print(response)
                print('--------------------------------------------')
            case '2': #dziala - wysyłanie katalogu
                print('--------------------------------------------')
                print('send whole directories to the server')
                path: str = input('Specify path to the directory: ')
                response = client.store(path, f'{config['username']}')
                print('--------------------------------------------')
            case '3':
                print('download files from the server')
            case '4':
                print('download directories from the server')
            case '5': #dziala
                print('list your uploaded files')
                ls, response = client.list_data(f'/{config['username']}')  # list data
                print(ls)
            case '6':
                print('synchronize data')
            case '7':
                print('delete selected uploaded files')
            case '8':
                print('delete all of your uploaded files')
            case '9':
                exit()
            case _:
                client.close_connection()
                print('Wrong option!')


def cli(args) -> None:
    #print(args)
    config: json = json.load(open('config.json', 'r'))
    if args.username:
        config['username'] = args.username
        with open('config.json', 'w') as cfg:
            cfg.write(json.dumps(config, indent='\t'))

    if not server_check(config):
        print('There is no specified server, edit config.json')
        exit()
    if not user_check(config):
        print('There is no username set, run with -u <username>')
        exit()

    client = TcpClient()
    if args.verify:
        server_response = client.verify_token()
        if server_response == -1:
            print("Authentication failure, run with -p to receive token")
        else:
            print("Token correct!")
        exit()
    if args.password:
        client.get_auth_token()

    exit()







#reading arg
parser = argparse.ArgumentParser(
                    prog='py-backapp',
                    description='This is the client side of py-backapp',
                    epilog='CLI mode is default, if you want to use interactive mode, specify the flag')
parser.add_argument('-i', '--interactive', action='store_true')
parser.add_argument('-u', '--username')
parser.add_argument('-p', '--password', action='store_true')
parser.add_argument('-v', '--verify', action='store_true')
parser.add_argument('-f', '--sendfile')
parser.add_argument('-F', '--downloadfile')
parser.add_argument('-d', '--senddir')
parser.add_argument('-D', '--downloaddir')
parser.add_argument('-l', '--list')
parser.add_argument('-s', '--synchronize')
parser.add_argument('-r', '--removefile')
parser.add_argument('-R', '--removeall')
args = parser.parse_args()

try:
    if args.interactive:
        menu()
    else:
        cli(args)
except KeyboardInterrupt:
    print('\nExiting...')
    exit()
except socket_error as err:
    print(socket_error)
    exit(-1)





# response = client.store('../screenshots', 'test/folder')  # dir transfer

# response = client.get('/test/test2/LICENSE', './')  # get file
# response = client.get('/test', './', True)  # get dir

# ls, response = client.list_data('/test/folder/screenshots')  # list data
# print(ls)

# print(f'local modification date: {datetime.fromtimestamp(os.path.getmtime("../screenshots/docker_1.png"))}')
# mod_date, response = client.get_modification_date('/test/folder/screenshots/docker_1.png')  # get modification date
# print(mod_date)

# response = client.delete('/')  # delete all data on the server

#print(response)
