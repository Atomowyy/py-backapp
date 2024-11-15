#!/usr/bin/env python3

import argparse

from backapp_helpers import *
from backapp_synchronization import *

from tcp_client import TcpClient
from backapp_interactive import interactive_mode

from socket import error as socket_error


# reading args
parser = argparse.ArgumentParser(
    prog='backapp.py',
    description='This is the client side of py-backapp, backup and synchronize your files with the server.'
                'If no argument is specified the program starts in interactive mode',
    epilog='source code: https://github.com/Atomowyy/py-backapp')
parser.add_argument('-i', '--interactive', action='store_true', help='start py-backapp in interactive mode')
parser.add_argument('--username', help='set username in config.json')
parser.add_argument('--server', help='set server in config.json')
parser.add_argument('--port', help='set port in config.json')
parser.add_argument('-g', '--gettoken', action='store_true', help='authorize user on the server and get a token')
parser.add_argument('-v', '--verifytoken', action='store_true', help='verify if current token is valid')

parser.add_argument('--local', help='path to local resource')
parser.add_argument('--remote', help='path to remote resource')

parser.add_argument('-l', '--list', action='store_true', help='list contents of remote dir')
parser.add_argument('-r', '--remove', action='store_true', help='remove remote resources')
parser.add_argument('-R', '--removeall', action='store_true', help="remove all users' remote resources")

parser.add_argument('-u', '--upload', action='store_true', help='upload local resources to the server')
parser.add_argument('-d', '--download', action='store_true', help='download remote resources from the server')

parser.add_argument('-s', '--syncfile', action='store_true', help='compare local and remote file and get the newer one')
parser.add_argument('-S', '--syncdir', action='store_true', help='synchronize local directory with the remote one')
cli_args = parser.parse_args()


def cli(args) -> None:
    config: json = load_config()
    config_modified = False

    # modifying config
    if args.username:
        config['username'] = args.username
        config_modified = True
    if args.server:
        config['server'] = args.server
        config_modified = True
    if args.port:
        config['port'] = args.port
        config_modified = True

    # save config if needed
    if config_modified:
        dump_config(config)
        exit(0)

    # check if something in config.json is not set
    config_correct = True
    if not server_check(config):
        print('There is no server specified, run with --server <server>')
        config_correct = False
    if not port_check(config):
        print('There is no port specified, run with --port <port>')
        config_correct = False
    if not user_check(config):
        print('There is no user specified, run with --username <username>')
        config_correct = False

    if not config_correct:
        exit(-1)

    # load config and initialize socket
    TcpClient.load_config()
    client = TcpClient()

    if args.verifytoken:
        server_response = client.verify_token()
        if server_response == -1:
            print("Authentication failure, run with -g to receive token")
        else:
            print("Token correct")
        exit(server_response)

    if args.gettoken:
        server_response = client.get_auth_token()
        if server_response == -1:
            print("Authentication failure")
        else:
            print("Authentication success")
        exit(server_response)

    ##############################################
    # backup and sync

    # token needs to ve valid for following actions
    server_response = client.verify_token()
    if server_response == -1:
        print("Authentication failure, run with -g to receive token")
        exit(-1)

    # initialize new socket and send token
    client = TcpClient()
    client.send_auth_token()

    # get remote and local paths
    remote_path = args.remote
    local_path = args.local

    # check remote path
    if remote_path is None:
        print('Remote path not specified, run with --remote <remote_path>')
        exit(-1)

    if args.list:
        ls, response = client.list_data(remote_path)
        print(ls)
        exit(0)
    if args.remove:
        response = client.delete(remote_path)
        print(response)
        exit(0)
    if args.removeall:
        response = client.delete('/')
        print(response)
        exit(0)

    # check local path
    if local_path is None:
        print('Local path not specified, run with --local <local_path>')
        exit(-1)
    if not os.path.exists(local_path):
        print('Local path is invalid')
        exit(-1)

    if args.upload:
        response = client.store(local_path, remote_path)
        print(response)
        exit(0)
    if args.download:
        response = client.get(remote_path, local_path)
        print(response)
        exit(0)

    if args.syncfile:
        if not os.path.isfile(local_path):
            print('Local path is is not a file')
            exit(-1)

        ls_, response = client.list_data(
            f'{remote_path.replace(os.path.basename(remote_path), '')}'
        )

        if response == 'Invalid Path':
            print('Specified file/directory was not found on the server')
            exit(-1)

        synchronize_file_cli(local_path, remote_path, ls_)
        print('Files synchronized')
        exit(0)
    if args.syncdir:
        if not dir_exists(local_path):
            print('Local path is is not a directory')
            exit(-1)

        ls_, response = client.list_data(remote_path)

        if response == 'Invalid Path':
            print('Specified remote file/directory was not found on the server')
            exit(-1)

        synchronize_dir(local_path, remote_path, ls_)
        print('Directories synchronized')
        exit(0)

    exit(0)


try:
    if cli_args.interactive or len(sys.argv) == 1:  # run interactively by default or if '-i' flag is specified
        interactive_mode()
    else:
        cli(cli_args)
except KeyboardInterrupt:
    print('\nExiting...')
    exit()
except socket_error as err:
    print(err)
    exit(-1)
