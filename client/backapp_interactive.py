from backapp_helpers import *
from backapp_synchronization import *
from tcp_client import TcpClient

# colors
# reset - \33[0m
# info - \33[34m
# input - \33[32m
# warning - \33[33m
# error - \33[31m
# success - \33[92m

# menu options
menu = [
    '1.Send files to the server',
    '2.Send directories to the server',
    '3.Download files/directories from the server',
    '4.List your uploaded files',
    '5.Synchronize file',
    '6.Synchronize directory',
    '7.Delete uploaded files/directories',
    '8.Delete all user data',
    '9.Exit',
]


def get_arrow_key() -> str:
    # arrow up -> \033[A
    # arrow down -> \033[A

    key = get_key()  # Read the first character
    if key == '\033':
        key += get_key()  # '[' character
        key += get_key()  # the arrow key code
    return key


def clear_screen() -> None:
    # ANSI code to move cursor to home and clear screen
    sys.stdout.write("\033[H\033[J")


def print_menu(selected_index) -> None:
    clear_screen()
    sys.stdout.flush()
    sys.stdout.write('\n')

    for idx, option in enumerate(menu):
        if idx == selected_index:
            # \33[34m - blue, \33[1m - bold
            sys.stdout.write(f"\33[34m\33[1m> {option} \33[5m👈\n\33[0m")  # highlight the selected option
        else:
            sys.stdout.write(f"  {option}\n")
    sys.stdout.flush()


def wait_for_user_input() -> None:
    print('\nPress any key to continue...')
    get_key()


def handle_action(action_idx, username):
    client = TcpClient()
    client.send_auth_token()

    match action_idx:
        case 0:  # store file
            local_path: str = get_input('Local file path: ')
            remote_path: str = get_input('Remote file path: ')
            response = client.store(local_path, remote_path)
            print(response)
        case 1:  # store dir
            local_path: str = get_input('Local dir path: ')
            remote_path: str = get_input('Remote dir path: ')
            response = client.store(local_path, remote_path)
            print(response)
        case 2:  # download file/dir
            remote_path: str = get_input('Remote path: ')
            user_path: str = get_input('Local dir path [default: ./Downloads]: ')
            local_path: str = './Downloads' if user_path == '' else user_path
            response = client.get(remote_path, local_path)
            print(response)
        case 3:  # listing data
            user_path: str = get_input('Remote dir path [default: /]: ')
            remote_path: str = '/' if user_path == '' else user_path
            ls, response = client.list_data(remote_path)
            print(ls)
        case 4:  # file sync
            local_path = get_input('Local file path: ')
            if not file_exists(local_path):
                client.close_connection()
                return

            remote_path = get_input('Specify remote file path: ')

            ls_, response = client.list_data(
                f'{remote_path.replace(os.path.basename(remote_path), '')}'
            )

            if response == 'Invalid Path':
                print('\33[33mSpecified file/directory was not found on the server\33[0m')
                return

            synchronize_file(local_path, remote_path, ls_)

        case 5:  # dir sync
            local_path = get_input('Local directory path: ')
            if not dir_exists(local_path):
                client.close_connection()
                return

            remote_path = get_input('Remote directory path: ')

            ls_, response = client.list_data(f'{remote_path}')

            if response == 'Invalid Path':
                print('\33[33mSpecified remote file/directory was not found on the server\33[0m')
                return

            synchronize_dir(local_path, remote_path, ls_)

        case 6:  # deleting
            remote_path: str = get_input('Remote path: ')
            response = client.delete(remote_path)
            print(response)
        case 7:  # delete all user data
            response = client.delete('/')
            print(response)
        case 8:  # exit
            exit()
        case _:  # default
            client.close_connection()
            print('Wrong option')


def case_spacer() -> None:
    print('\n\33[34m--------------------------------------------\33[0m\n')


def interactive_mode() -> None:
    config = load_config()

    if not server_check(config):
        server_set(config)
    if not user_check(config):
        user_set(config)

    TcpClient.load_config()  # load config.json into TcpClient

    username = TcpClient.username

    client = TcpClient()
    server_response = client.verify_token()

    if server_response == -1:
        while server_response == -1:
            print("\33[33mAuthentication failure\33[0m")
            client = TcpClient()
            server_response = client.get_auth_token()
    print("\33[92mAuthenticated successfully\33[0m")

    ##############################################
    #  user authenticated
    print(f'\33[34mHello {username}\33[0m')
    wait_for_user_input()

    current_index = 0
    while True:
        print_menu(current_index)

        key = get_arrow_key()

        if key in ('\033[A', 'w'):  # up arrow / w
            current_index -= 1
            current_index %= len(menu)
        elif key in ('\033[B', 's'):  # down arrow / s
            current_index += 1
            current_index %= len(menu)
        elif key in [str(x) for x in range(1, len(menu) + 1)]:
            current_index = int(key) - 1
        elif key == '\n':  # Enter - option selected
            if current_index == len(menu) - 1:
                exit(0)

            case_spacer()
            handle_action(current_index, username)
            case_spacer()

            wait_for_user_input()
