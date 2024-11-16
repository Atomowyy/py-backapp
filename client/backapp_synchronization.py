import os
from datetime import datetime, UTC
from tcp_client import TcpClient
from backapp_helpers import get_input


def synchronize_file(local_path, remote_path, remote_ls_) -> None:
    filename = os.path.basename(local_path)
    remote_filename = os.path.basename(remote_path)

    if filename != remote_filename:
        print('\33[33mLocal filename and remote filename do not match\33[0m')
        return

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


def synchronize_file_cli(local_path, remote_path, remote_ls_) -> None:
    filename = os.path.basename(local_path)
    remote_filename = os.path.basename(remote_path)

    if filename != remote_filename:
        print('Local filename and remote filename names do not match')
        return

    local_mod_date = datetime.fromtimestamp(os.path.getmtime(local_path), UTC)

    ls = remote_ls_.split('  ')

    if filename in ls:
        print(
            f'Local modification date: {local_mod_date}')
        client = TcpClient()
        client.send_auth_token()
        remote_mod_date, response = client.get_modification_date(
            f'/{remote_path}'
        )
        print(f'Remote modification date: {remote_mod_date}')

        if local_mod_date == remote_mod_date:
            print('Files are up to date')
        elif local_mod_date > remote_mod_date:
            print('Remote file is older than local')
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
            print('Downloading files from the server...')
            client = TcpClient()
            client.send_auth_token()
            response = client.get(
                remote_path,
                local_path.replace(os.path.basename(local_path), '')
            )
            print(response)
    else:
        print('Specified filename was not found on the server')


def synchronize_dir(local_path, remote_path, remote_ls_) -> None:
    local_ls = os.listdir(local_path)
    remote_ls = remote_ls_.split('  ')

    files_dirs_to_compare = set(local_ls + remote_ls)
    # store/get missing items
    for item in {x for x in files_dirs_to_compare}:
        local_item_path = f'{local_path.rstrip('/')}/{item}'
        remote_item_path = f'{remote_path.rstrip('/')}/{item}'

        if item not in remote_ls:
            files_dirs_to_compare.discard(item)

            client = TcpClient()
            client.send_auth_token()

            print(f"Uploading: {local_item_path}")
            client.store(local_item_path, remote_path)
        elif item not in local_ls:
            files_dirs_to_compare.discard(item)

            client = TcpClient()
            client.send_auth_token()

            print(f"Downloading: {remote_item_path}")
            client.get(remote_item_path, local_path)

    # compare modification dates
    for item in files_dirs_to_compare:
        local_item_path = f'{local_path.rstrip('/')}/{item}'
        remote_item_path = f'{remote_path.rstrip('/')}/{item}'

        client = TcpClient()
        client.send_auth_token()

        # check if item is a directory
        ls_, response = client.list_data(remote_item_path)
        if ls_ != '':  # some recursion magic 🪄
            synchronize_dir(local_item_path, remote_item_path, ls_)
            continue

        client = TcpClient()
        client.send_auth_token()

        local_mod_date = datetime.fromtimestamp(os.path.getmtime(local_item_path), UTC)
        remote_mod_date, _ = client.get_modification_date(remote_item_path)

        if local_mod_date == remote_mod_date:
            continue
        elif local_mod_date > remote_mod_date:
            client = TcpClient()
            client.send_auth_token()

            print(f"Uploading: {local_item_path}")
            client.store(local_item_path, remote_path)
        elif local_mod_date < remote_mod_date:
            client = TcpClient()
            client.send_auth_token()

            print(f"Downloading: {remote_item_path}")
            client.get(remote_item_path, local_path)
