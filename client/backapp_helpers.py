import os
import sys
import json

if sys.platform == 'win32':
    import msvcrt
else:
    import termios

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')


def get_key_unix() -> str:
    """Read a single character from the keyboard. (Unix)"""
    fd = sys.stdin.fileno()  # get file descriptor associated with file-like object (stdin, stdout, stderr)
    old_settings = termios.tcgetattr(fd)  # Get current terminal settings

    # terminal settings - canonical mode, disable echo, keep interrupts
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
    try:
        # tty.setraw(fd)  # Set terminal to raw mode
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        ch = sys.stdin.read(1)  # Read one byte
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_key_windows() -> bytes:
    """Read a single character from the keyboard. (Windows)"""
    key = msvcrt.getch()
    if key == b'\x03':  # ctrl + c
        print('Exiting...')
        exit()
    return key


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


def get_input(message) -> str:
    user_input = input(message + '\33[32m')
    print('\33[0m', end='')  # reset text coloring
    return user_input


def load_config() -> json:
    return json.load(open(CONFIG_PATH, 'r'))


def dump_config(config):
    with open(CONFIG_PATH, 'w') as cfg:
        cfg.write(json.dumps(config, indent='\t'))


def server_check(config: json) -> bool:
    server: str = config['server']
    return server != ''


def port_check(config: json) -> bool:
    port: str = config['port']
    return port != ''


def user_check(config: json) -> bool:
    username = config['username']
    return username != ''


def server_set(config) -> None:
    print('\33[33mServer not specified, please enter valid server address\33[0m')
    config['server'] = str(get_input('Server address: '))


def port_set(config) -> None:
    print('\33[33mServer port not specified, please enter valid port number\33[0m')
    config['port'] = str(get_input('Port: '))


def user_set(config) -> None:
    print("\33[33mUsername not specified, please enter valid username\33[0m")
    config['username'] = str(get_input('Username: '))
