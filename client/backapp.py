from socket import error as socket_error
from tcp_client import TcpClient
from datetime import datetime, UTC
import os
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
    print('3.Download files/directories from the server')
    print('4.List your uploaded files')
    print('5.Synchronize file')
    print('6.Synchronize directory')
    print('7.Delete selected uploaded files')
    print('8.Delete all of your uploaded files')
    print('9.Exit')


def menu() -> None:
    # verifying JSON
    config: json = json.load(open('config.json', 'r'))

    if not server_check(config):
        print('There is no specified server, please enter valid IP address and port number')
        server_set(config)
    if not user_check(config):
        print("There is no user logged in.")
        user_set(config)

    TcpClient.load_config()
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
            case '1':  # dziala - wysyłanie pliku
                print('--------------------------------------------')
                local_path: str = input('Specify path to the file: ')
                response = client.store(local_path, f'{config['username']}')
                print(response)
                print('--------------------------------------------')
            case '2':  # dziala - wysyłanie katalogu
                print('--------------------------------------------')
                local_path: str = input('Specify path to the directory: ')
                response = client.store(local_path, f'{config['username']}')
                print(response)
                print('--------------------------------------------')
            case '3':  # - pobieranie pliku/folderu - działa, do poprawy, dodać try
                print('--------------------------------------------')
                filename: str = input(
                    'Specify path to the file/directory that you want to download: ')
                response = client.get(f'/{config['username']}/{filename}', './Downloads')
                print(response)
                print('--------------------------------------------')
            case '4':  # dziala
                print('list your uploaded files')
                ls, response = client.list_data(f'/{config['username']}')  # list data
                print(ls)
            case '5':
                local_path = os.path.abspath(
                    './' + input('Specify local path to the file that you want to synchronise: '))
                remote_path = input('Specify remote path to the file that you want to synchronise: ')

                if not os.path.isfile(local_path):
                    print('File does not exist')
                    client.close_connection()
                    continue

                filename = os.path.basename(local_path)
                local_mod_date = datetime.fromtimestamp(os.path.getmtime(local_path), UTC)

                ls_, response = client.list_data(
                    f'/{config['username']}/{remote_path.replace(os.path.basename(remote_path), '')}'
                )

                if response == 'Invalid path':
                    print('Invalid remote path')
                    continue

                ls = ls_.split('  ')

                if filename in ls:
                    print(
                        f'Local modification date: {local_mod_date}')
                    client = TcpClient()
                    client.send_auth_token()
                    remote_mod_date, response = client.get_modification_date(f'/{config['username']}/{filename}')
                    print(f'Remote modification date: {remote_mod_date}')

                    if local_mod_date == remote_mod_date:
                        print('Files are up to date!')
                    elif local_mod_date > remote_mod_date:
                        print('Remote file is older than local')
                        decision = input('Do you want to upload current version to the server? [n/y]: ')
                        if decision.upper() in ('Y', 'YES'):
                            print('Sending files to the server...')
                            client = TcpClient()
                            client.send_auth_token()
                            response = client.store(
                                local_path,
                                f'{config['username']}/{remote_path.replace(os.path.basename(remote_path), '')}'
                            )
                            print(response)
                    elif local_mod_date < remote_mod_date:
                        print('Local file is older than remote')
                        decision = input('Do you want to download current version from the server? [n/y]: ')
                        print(decision.upper())
                        if decision.upper() in ('Y', 'YES'):
                            print('Downloading files from the server...')
                            client = TcpClient()
                            client.send_auth_token()
                            response = client.get(
                                f'/{config['username']}/{remote_path}',
                                local_path.replace(os.path.basename(local_path), '')
                            )
                            print(response)
                else:
                    print('Specified file/directory was not found on the server')

            case '6':
                local_path = input('Specify local path to the directory that you want to synchronise: ').rstrip('/')
                remote_path = input('Specify remote path to the directory that you want to synchronise: ')

                if not os.path.isdir(local_path):
                    print('Directory does not exist')
                    client.close_connection()
                    continue

                ls_, response = client.list_data(f'/{config['username']}/{remote_path}')

                if response == 'Invalid path':
                    print('Invalid remote path')
                    continue

                local_ls = os.listdir(local_path)
                remote_ls = ls_.split('  ')

                files_dirs_to_compare = local_ls + remote_ls
                # store/get missing items
                for item in local_ls + remote_ls:
                    if item not in remote_ls:
                        files_dirs_to_compare.remove(item)

                        client = TcpClient()
                        client.send_auth_token()
                        client.store(f'{local_path}/{item}', f'{config['username']}/{remote_path}')
                    elif item not in local_ls:
                        files_dirs_to_compare.remove(item)

                        client = TcpClient()
                        client.send_auth_token()
                        client.get(f'{config['username']}/{remote_path}/{item}', f'{local_path}')

                # compare modification dates
                for item in files_dirs_to_compare:
                    client = TcpClient()
                    client.send_auth_token()

                    local_mod_date = datetime.fromtimestamp(os.path.getmtime(local_path), UTC)
                    remote_mod_date, _ = client.get_modification_date(f'{config['username']}/{remote_path}/{item}')

                    if local_mod_date == remote_mod_date:
                        continue
                    elif local_mod_date > remote_mod_date:
                        client = TcpClient()
                        client.send_auth_token()
                        client.store(f'{local_path}/{item}', f'{config['username']}/{remote_path}')
                    elif local_mod_date < remote_mod_date:
                        client = TcpClient()
                        client.send_auth_token()
                        client.get(f'{config['username']}/{remote_path}/{item}', f'{local_path}')

                print('Directory synchronized successfully')
            case '7':  # usuwanie
                print('--------------------------------------------')
                local_path: str = input('Specify path to the file or folder that you want to delete: ')
                response = client.delete(f'/{config['username']}/{local_path}')
                print(response)
                print('--------------------------------------------')
            case '8':
                print('--------------------------------------------')
                response = client.delete(f'/{config['username']}/')
                print('--------------------------------------------')
                print(response)
            case '9':
                exit()
            case _:
                client.close_connection()
                print('Wrong option!')


def cli(args) -> None:
    # print(args)
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

    TcpClient.load_config()
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


# reading arg
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

# print(f'local modification date: {datetime.fromtimestamp(os.path.getmtime("../screenshots/docker_1.png"))}')
# mod_date, response = client.get_modification_date('/test/folder/screenshots/docker_1.png')  # get modification date
# print(mod_date)
