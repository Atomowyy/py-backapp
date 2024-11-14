import os
from datetime import datetime, UTC
from tcp_client import TcpClient
from backapp_helpers import get_input


def file_exists(file_path) -> bool:
    if not os.path.isfile(file_path):
        print('\33[33mFile does not exist\33[0m')
        return False
    return True


def dir_exists(dir_path) -> bool:
    if not os.path.isdir(dir_path):
        print('\33[33mDirectory does not exist\33[0m')
        return False
    return True


def synchronize_file(local_path, remote_path, remote_ls_):
    filename = os.path.basename(local_path)
    local_mod_date = datetime.fromtimestamp(os.path.getmtime(local_path), UTC)

    ls = remote_ls_.split('  ')

    if filename in ls:
        print(
            f'\33[34mLocal modification date: {local_mod_date}\33[0m')
        client = TcpClient()
        client.send_auth_token()
        remote_mod_date, response = client.get_modification_date(
            f'/{remote_path}'
        )
        print(f'\33[34mRemote modification date: {remote_mod_date}\33[0m')

        if local_mod_date == remote_mod_date:
            print('Files are up to date')
        elif local_mod_date > remote_mod_date:
            print('Remote file is older than local')
            decision = get_input('Do you want to upload current version to the server? [n/y]: ')
            if decision.upper() in ('Y', 'YES'):
                print('Sending files to the server...')
                client = TcpClient()
                client.send_auth_token()
                response = client.store(
                    local_path,
                    f'{remote_path.replace(os.path.basename(remote_path), '')}'
                )
                print(response)
        elif local_mod_date < remote_mod_date:
            print('Local file is older than remote')
            decision = get_input('Do you want to download current version from the server? [n/y]: ')
            if decision.upper() in ('Y', 'YES'):
                print('Downloading files from the server...')
                client = TcpClient()
                client.send_auth_token()
                response = client.get(
                    f'{remote_path}',
                    local_path.replace(os.path.basename(local_path), '')
                )
                print(response)
    else:
        print('\33[33mSpecified filename was not found on the server\33[0m')


def synchronize_dir(local_path, remote_path, remote_ls_):
    local_ls = os.listdir(local_path)
    remote_ls = remote_ls_.split('  ')

    files_dirs_to_compare = local_ls + remote_ls
    # store/get missing items
    for item in local_ls + remote_ls:
        if item not in remote_ls:
            files_dirs_to_compare.remove(item)

            client = TcpClient()
            client.send_auth_token()
            client.store(f'{local_path}/{item}', f'{remote_path}')
        elif item not in local_ls:
            files_dirs_to_compare.remove(item)

            client = TcpClient()
            client.send_auth_token()
            client.get(f'{remote_path}/{item}', f'{local_path}')

    # compare modification dates
    for item in files_dirs_to_compare:
        client = TcpClient()
        client.send_auth_token()

        local_mod_date = datetime.fromtimestamp(os.path.getmtime(local_path), UTC)
        remote_mod_date, _ = client.get_modification_date(f'{remote_path}/{item}')

        if local_mod_date == remote_mod_date:
            continue
        elif local_mod_date > remote_mod_date:
            client = TcpClient()
            client.send_auth_token()
            client.store(f'{local_path}/{item}', f'{remote_path}')
        elif local_mod_date < remote_mod_date:
            client = TcpClient()
            client.send_auth_token()
            client.get(f'{remote_path}/{item}', f'{local_path}')

    print('\33[92mDirectory synchronized successfully\33[0m')