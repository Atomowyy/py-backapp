import sys
import termios
import json


def get_key() -> str:
    """Read a single character from the keyboard."""
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


def get_input(message):
    user_input = input(message + '\33[32m')
    print('\33[0m', end='')  # reset text coloring
    return user_input


def load_config() -> json:
    return json.load(open('config.json', 'r'))


def user_check(config: json) -> bool:
    username = config['username']
    return username != ''


def server_check(config: json) -> bool:
    server: str = config['server']
    return server != ''


def dump_config(config):
    with open('config.json', 'w') as cfg:
        cfg.write(json.dumps(config, indent='\t'))


def server_set(config) -> None:
    print('\33[33mServer not specified, please enter valid server address and port number\33[0m')
    config['server'] = str(get_input('Server address: '))
    config['port'] = str(get_input('Server port: '))
    dump_config(config)


def user_set(config) -> None:
    print("\33[33mUsername not specified, please enter valid username\33[0m")
    config['username'] = str(get_input('Username: '))
    dump_config(config)

##############################################################
