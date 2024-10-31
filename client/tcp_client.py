import socket
import ssl
import json

import tarfile
import os

from datetime import datetime


class TcpClient:
    # load config from config.json
    config = json.load(open('config.json', 'r'))

    keys_to_check = {'server', 'port', 'username', 'token'}
    if not keys_to_check.issubset(config.keys()):
        raise Exception('Invalid client config file')

    server = config['server']
    port = int(config['port'])
    username = config['username']
    token = config['token']

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
        self.secure_socket.connect((self.server, self.port))

    def _send_command(self, command: bytes) -> None:
        self.secure_socket.sendall(command)

    def _get_response(self) -> str:
        return self.secure_socket.recv(1024).decode()

    def send_auth_token(self) -> str:
        self._send_command(ServerActions.authorize(self.username, self.token))
        return self._get_response()

    def verify_token(self) -> int:
        response = self.send_auth_token()

        if response == 'Access denied':
            self.secure_socket.close()
            return -1

        return 0

    def get_auth_token(self) -> int:
        password = input(f'Password for {self.config["username"]}: ')
        self._send_command(ServerActions.get_token(self.username, password))
        response = self._get_response()

        if response == 'Access denied':
            return -1

        # if authorization was successful -> you get a token
        self.config['token'] = response

        # dump config to config.json
        with open('config.json', 'w') as user_db:
            user_db.write(json.dumps(self.config, indent='\t'))

        return 0

    def store(self, path: str, server_path: str) -> str:
        self._send_command(ServerActions.store(server_path))

        socket_file = self.secure_socket.makefile(mode='wb')
        with tarfile.open(fileobj=socket_file, mode='w|') as socket_tar:
            socket_tar.add(path, arcname=os.path.basename(path))
        socket_file.flush()
        socket_file.close()

        return self._get_response()

    def get(self, server_path: str, extract_path: str, is_dir: bool = False) -> str:
        if is_dir:
            self._send_command(ServerActions.get_dir(server_path))
        else:
            self._send_command(ServerActions.get_file(server_path))

        socket_file = self.secure_socket.makefile('rb')
        with tarfile.open(fileobj=socket_file, mode='r|') as tar:
            tar.extractall(extract_path, filter='tar')

        return self._get_response()

    def get_dir(self, server_path: str, extract_path: str) -> str:
        self._send_command(ServerActions.get_dir(server_path))

        socket_file = self.secure_socket.makefile('rb')
        with tarfile.open(fileobj=socket_file, mode='r|') as tar:
            tar.extractall(extract_path, filter='tar')

        return self._get_response()

    def list_data(self, server_path: str) -> tuple[str, str]:
        self._send_command(ServerActions.list_data(server_path))

        listing = self._get_response()
        response = self._get_response()
        return listing, response

    def get_modification_date(self, server_path: str) -> tuple[datetime, str]:
        self._send_command(ServerActions.get_modification_date(server_path))

        modification_date = datetime.fromisoformat(self._get_response())
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
    def store(cls, path: str) -> bytes:
        return ('STORE' + cls.spacer + path).encode()

    @classmethod
    def get_file(cls, file_path: str) -> bytes:
        return ('GET FILE' + cls.spacer + file_path).encode()

    @classmethod
    def get_dir(cls, dir_path: str) -> bytes:
        return ('GET DIR' + cls.spacer + dir_path).encode()

    @classmethod
    def get_modification_date(cls, path: str) -> bytes:
        return ('GET MODIFICATION DATE' + cls.spacer + path).encode()

    @classmethod
    def delete(cls, path: str) -> bytes:
        return ('DELETE DATA' + cls.spacer + path).encode()

    @classmethod
    def list_data(cls, path: str) -> bytes:
        return ('LIST DATA' + cls.spacer + path).encode()
