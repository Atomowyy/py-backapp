import socket
import ssl
import select

import os
import shutil
from datetime import datetime, UTC, timedelta

import tarfile
import json
import hashlib
import secrets


class TcpServer:
    project_path = os.path.abspath('./')
    data_dir = project_path + '/data'

    @classmethod
    def get_host_ip(cls):
        return socket.gethostbyname(socket.gethostname())

    @staticmethod
    def generate_user_token(username) -> tuple[str, dict[str, str]]:
        # create a 128-digit token (64 hex numbers)
        token = secrets.token_hex(64)

        token_metadata = {
            'username': username,
            'expiration': datetime.now(UTC) + timedelta(hours=1),
        }

        return token, token_metadata

    def __init__(self, certfile, keyfile, port=1234, backlog=0, tcp_buffer_size=32_768):
        # create data dir if not present
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.port = port
        self.backlog = backlog
        self.tcp_buffer_size = tcp_buffer_size

        # check if cert and key file exist
        if (not os.path.isfile(certfile)) or (not os.path.isfile(keyfile)):
            raise Exception("Certfile and keyfile must be provided")

        self.certfile = certfile
        self.keyfile = keyfile

        self.server_socket = None
        self.context = None
        self.secure_socket = None

        self.users = json.load(open('users_db.json', 'r'))  # load users db
        self.access_tokens = dict()

    def run(self):
        # create server socket
        # AF_INET - IPv4, SOCK_STREAM - TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind socket to all available ipv4 interfaces and PORT
        self.server_socket.bind(('', self.port))

        # allow socket to reuse the address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # set socket timeout in seconds
        self.server_socket.settimeout(30)

        # set server to non-blocking mode
        self.server_socket.setblocking(False)

        # start listening and set backlog
        self.server_socket.listen(self.backlog)

        # wrapp the socket with SSL
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2  # set minimum TLS version to 1.2
        # load cert and key files
        self.context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        # waiting for connections
        print(f'Started py-backapp server on {self.get_host_ip()}:{self.port}')
        while True:
            # wait for incoming connections with 1s timeout
            readable, _, _ = select.select([self.server_socket], [], [], 1)

            # for each readable socket
            for s in readable:
                try:
                    client_socket, client_address = s.accept()
                    self._handle_connection(client_socket, client_address)
                except socket.error as err:
                    print(f'\tSocket error: {err}')

    def close_server_socket(self):
        self.server_socket.close()

    def _handle_connection(self, client_socket, client_address):
        # secure client socket with ssl
        self.secure_socket = self.context.wrap_socket(client_socket, server_side=True)
        # print connection info
        print(f'Connected with {client_address[0]}:{client_address[1]}, TLS version: {self.secure_socket.version()}')

        try:
            # receive authentication - 'GET TOKEN/AUTHENTICATE <> user <> pass/token'
            auth = self.secure_socket.recv(self.tcp_buffer_size).decode()
            auth_status = self._handle_authentication_and_token_creation(auth)

            if auth_status == -1:
                self._send_response('Authentication failed')
                self.secure_socket.close()
                return
            elif auth_status == 0:
                self._send_response('Authentication successful', False)
            elif auth_status == 1:
                self._send_response('Token created successfully')
                return

            # receive header from the client
            header = self.secure_socket.recv(self.tcp_buffer_size).decode()

            # unpack action and argument from header
            action, argument = header.split(ServerActions.spacer)
            print(f'\tAction: {action}, argument: {argument}')

            if '..' in argument:  # moving outside data_dir
                raise ValueError('".." not allowed in argument (path to resource)')

            # handle server action and store response for the client
            response = self._handle_server_action(action, argument)

            # send response to the client
            self._send_response(response)
        except ValueError as err:
            self._send_response('Invalid Request')
            print(f'\tValueError: {err}')

        except socket.error as err:
            print(f'\tSocket error: {err}')

        finally:
            self.secure_socket.close()

    # TODO: implement
    def _handle_authentication_and_token_creation(self, auth: str):
        action, user, auth_method = auth.split(ServerActions.spacer)

        if user not in self.users:
            return -1

        if action == 'GET TOKEN':
            # authenticate user
            user_password = self.users[user]
            sent_password = hashlib.sha512(auth_method.encode()).hexdigest()

            if sent_password != user_password:
                return -1

            # generate token
            token, token_metadata = self.generate_user_token(user)

            # store token
            self.access_tokens[token] = token_metadata

            # send token to the client
            self._send_response(token, False)

            return 1

        elif action == 'AUTHENTICATE':
            provided_token = auth_method

            if provided_token not in self.access_tokens:
                return -1

            # get token metadata
            token_metadata = self.access_tokens[provided_token]

            # check if token is for the right user
            if token_metadata['username'] != user:
                return -1

            # check if token expired
            if datetime.now(UTC) > token_metadata['expiration']:
                return -1

            return 0

    def _send_response(self, response: str, print_response: bool = True) -> None:
        response_str = str(response)
        self.secure_socket.sendall(response_str.encode())
        if print_response:
            print('\t' + response_str)

    def _handle_server_action(self, action: str, argument: str) -> str:
        response = 'Action Accepted'  # default response
        match action:
            case 'STORE':
                try:
                    self._handle_storing(argument)
                except tarfile.TarError:
                    response = 'Something went wrong'
            case 'GET FILE':
                result = self._handle_file_retrieving(argument)
                if result == -1:
                    response = 'Invalid Path'
            case 'GET DIR':
                result = self._handle_dir_retrieving(argument)
                if result == -1:
                    response = 'Invalid Path'
            case 'GET MODIFICATION DATE':
                result = self._handle_getting_modification_date(argument)
                if result == -1:
                    response = 'Invalid Path'
            case 'DELETE DATA':
                result = self._handle_deleting(argument)
                if result == -1:
                    response = 'Provided path does not exist'
            case 'LIST DATA':
                result = self._handle_listing(argument)
                if result == -1:
                    response = 'Invalid Path'
            case _:
                response = 'Action Denied!'

        return response

    def _handle_storing(self, save_path: str) -> int:
        # add '/' to the beginning if necessary
        if save_path[0] != '/':
            save_path = '/' + save_path

        full_save_path = self.data_dir + save_path

        # create directories if they don't exist
        os.makedirs(full_save_path, exist_ok=True)

        socket_file = self.secure_socket.makefile('rb')
        with tarfile.open(fileobj=socket_file, mode='r|') as socket_tar:
            socket_tar.extractall(full_save_path, filter='tar')

        return 0

    def _send_tar(self, path: str):
        socket_file = self.secure_socket.makefile('wb')
        try:
            with tarfile.open(fileobj=socket_file, mode='w|') as socket_tar:
                socket_tar.add(path, arcname=os.path.basename(path))
                return 0
        except tarfile.TarError:
            return -1

    def _handle_file_retrieving(self, file_path: str) -> int:
        # print(f'\tSending file {file_path}')
        full_path = self.data_dir + file_path

        if not os.path.isfile(full_path):
            return -1

        return self._send_tar(full_path)

    def _handle_dir_retrieving(self, dir_path):
        # print(f'\tSending dir {dir_path}')
        full_path = self.data_dir + dir_path

        if not os.path.isdir(full_path):
            return -1

        return self._send_tar(full_path)

    def _handle_getting_modification_date(self, path):
        # print(f'\tSending modification date of {path}')
        full_path = self.data_dir + path

        if not os.path.exists(full_path):
            return -1

        # get the modification time timestamp
        modification_time = os.path.getmtime(full_path)

        # convert it to string & human-readable format
        modification_date = str(datetime.fromtimestamp(modification_time))
        print(f'\tModification date is {modification_date}')

        self._send_response(modification_date, False)

        return 0

    def _handle_deleting(self, path: str) -> int:
        # print(f'\tDeleting data in {path}')
        full_path = self.data_dir + path

        if not os.path.exists(full_path):
            return -1

        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

        return 0

    def _handle_listing(self, path: str) -> int:
        # print(f'\tListing data in {path}')
        full_path = self.data_dir + path

        if not os.path.exists(full_path):
            return -1

        listing = '  '.join(os.listdir(full_path))
        self._send_response(listing, False)
        return 0


class ServerActions:
    spacer = '<;;;>'

    @classmethod
    def get_token(cls, user: str, password: str) -> bytes:
        return ('GET TOKEN' + cls.spacer + user + cls.spacer + password).encode()

    @classmethod
    def authenticate(cls, user: str, token: str) -> bytes:
        return ('AUTHENTICATE' + cls.spacer + user + cls.spacer + token).encode()

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
