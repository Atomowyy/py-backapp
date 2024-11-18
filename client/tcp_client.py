import socket
import ssl
import json
import sys

import tarfile
import os

from datetime import datetime

from backapp_helpers import get_key_unix, get_key_windows, load_config


class TcpClient:
    config = None
    server = None
    port = None
    username = None
    token = None

    @classmethod
    def load_config(cls) -> None:
        # load config from config.json
        TcpClient.config = load_config()

        keys_to_check = {'server', 'port', 'username', 'token'}
        if not keys_to_check.issubset(TcpClient.config.keys()):
            raise Exception('Invalid client config file')

        TcpClient.server = TcpClient.config['server']
        TcpClient.port = TcpClient.config['port']
        TcpClient.username = TcpClient.config['username']
        TcpClient.token = TcpClient.config['token']

    def __init__(self, verify_certificate: bool = False):
        # create client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # create ssl context
        context = ssl.create_default_context()

        # disable certificate verification (required for self-signed certificates to work properly)
        if verify_certificate is False:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        # wrap client socket with ssl
        self.secure_socket = context.wrap_socket(client_socket)

        # connect to the server
        self.secure_socket.connect((self.server, int(self.port)))

    def close_connection(self) -> None:
        self.secure_socket.close()

    def _send_command(self, command: bytes) -> None:
        self.secure_socket.sendall(command)

    def _get_response(self) -> str:
        return self.secure_socket.recv(1024).decode()

    def send_auth_token(self) -> int:
        self._send_command(ServerActions.authorize(self.username, self.token))
        response = self._get_response()

        if response == 'Access Denied':
            self.secure_socket.close()
            return -1

        return 0

    def verify_token(self) -> int:
        self._send_command(ServerActions.verify_token(self.username, self.token))
        response = self._get_response()

        if response == 'Access Denied':
            self.secure_socket.close()
            return -1

        return 0

    def get_auth_token(self) -> int:
        print(f'Password for {self.config["username"]}: ')
        password = ''
        try:
            # get password and dont display it in console
            while True:
                key = get_key_windows().decode(errors='replace') if sys.platform == 'win32' else get_key_unix()
                if key == '\r' or key == '\n':
                    break
                password += key
        except KeyboardInterrupt:
            print('Exiting...')
            exit(-1)

        self._send_command(ServerActions.get_token(self.username, password))
        del password
        response = self._get_response()

        if response == 'Access Denied':
            return -1

        # if authorization was successful -> you get a token
        TcpClient.config['token'] = response
        TcpClient.token = response

        # dump config to config.json
        with open('config.json', 'w') as user_db:
            user_db.write(json.dumps(self.config, indent='\t'))

        return 0

    def store(self, path: str, server_path: str) -> str:
        self._send_command(ServerActions.store(server_path))

        socket_file = self.secure_socket.makefile(mode='wb')
        try:
            with tarfile.open(fileobj=socket_file, mode='w|') as socket_tar:
                socket_tar.add(path, arcname=os.path.basename(path))
        except tarfile.TarError:
            return 'Invalid Path'

        return self._get_response()

    def get(self, server_path: str, extract_path: str) -> str:
        self._send_command(ServerActions.get(server_path))

        socket_file = self.secure_socket.makefile('rb')
        try:
            with tarfile.open(fileobj=socket_file, mode='r|') as socket_tar:
                socket_tar.extractall(extract_path, filter='tar')
        except tarfile.TarError:
            return 'Invalid Path'

        return self._get_response()

    def list_data(self, server_path: str) -> tuple[str, str]:
        self._send_command(ServerActions.list_data(server_path))

        listing = self._get_response()

        if listing == 'Invalid Path':
            return '', listing

        response = self._get_response()
        return listing, response

    def get_modification_date(self, server_path: str) -> tuple[datetime, str]:
        self._send_command(ServerActions.get_modification_date(server_path))

        tmp = self._get_response()
        if tmp == 'Invalid Path':
            return datetime(1800, 1, 1), tmp

        modification_date = datetime.fromisoformat(tmp)
        response = self._get_response()
        return modification_date, response

    def delete(self, server_path: str) -> str:
        self._send_command(ServerActions.delete(server_path))

        return self._get_response()


class ServerActions:
    spacer = '<;;;>'

    @classmethod
    def get_token(cls, user: str, password: str) -> bytes:
        return ('GET TOKEN' + cls.spacer + user + cls.spacer + password).encode()

    @classmethod
    def authorize(cls, user: str, token: str) -> bytes:
        return ('AUTHORIZE' + cls.spacer + user + cls.spacer + token).encode()

    @classmethod
    def verify_token(cls, user: str, token: str) -> bytes:
        return ('VERIFY TOKEN' + cls.spacer + user + cls.spacer + token).encode()

    @classmethod
    def store(cls, path: str) -> bytes:
        return ('STORE' + cls.spacer + path).encode()

    @classmethod
    def get(cls, path: str) -> bytes:
        return ('GET' + cls.spacer + path).encode()

    @classmethod
    def get_modification_date(cls, path: str) -> bytes:
        return ('GET MODIFICATION DATE' + cls.spacer + path).encode()

    @classmethod
    def delete(cls, path: str) -> bytes:
        return ('DELETE DATA' + cls.spacer + path).encode()

    @classmethod
    def list_data(cls, path: str) -> bytes:
        return ('LIST DATA' + cls.spacer + path).encode()
