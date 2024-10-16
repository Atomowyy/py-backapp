import socket
import ssl
import select

import os
import shutil

import zipfile


class TcpServer:
    project_path = os.path.abspath('./')
    data_dir = project_path + '/data'
    tmp_dir = project_path + '/tmp'
    tmp_file_path = tmp_dir + '/tmp_file'

    @classmethod
    def get_host_ip(cls):
        return socket.gethostbyname(socket.gethostname())

    def __init__(self, certfile, keyfile, port=1234, backlog=0, tcp_buffer_size=32_768):
        # create required directories if not present
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self._remove_tmp_file()

        self.port = port
        self.backlog = backlog
        self.tcp_buffer_size = tcp_buffer_size

        # check if cert and key file exist
        if (not os.path.isfile(certfile)) or (not os.path.isfile(keyfile)):
            raise Exception("Certfile and keyfile must be provided")

        self.certfile = certfile
        self.keyfile = keyfile

        self.context = None
        self.server_socket = None
        self.secure_socket = None

    def run(self):
        # create server socket
        # AF_INET - IPv4, SOCK_STREAM - TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind socket to all available ipv4 interfaces and PORT
        self.server_socket.bind(('', self.port))

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
            # receive action from the client
            action, argument = self.secure_socket.recv(self.tcp_buffer_size).decode().split(ServerActions.spacer)
            print(f'\tAction: {action}, argument: {argument}')

            if '..' in argument:  # moving outside data_dir
                self._send_response('Invalid Path')
                return

            # save data from client to tmp file
            self._save_recv_to_tmp_file()

            # handle server action and store response for the client
            response = self._handle_server_action(action, argument)

            # remove tmp file if it exists
            self._remove_tmp_file()

            # send response to the client
            self._send_response(response)

        except socket.error as err:
            print(f'\tSocket error: {err}')

        finally:
            self.secure_socket.close()

    def _send_response(self, response) -> None:
        self.secure_socket.sendall(response.encode())
        print('\t' + response)

    def _save_recv_to_tmp_file(self) -> None:
        while True:
            # receive data
            data = self.secure_socket.recv(self.tcp_buffer_size)
            if not data or data == ServerActions.end_transfer:
                break

            # store data in tmp file
            with open(self.tmp_file_path, 'ab') as tmp_file:
                tmp_file.write(data)

    def _handle_server_action(self, action, argument) -> str:
        # TODO: determine what to do based on the received action
        response = 'Action Accepted'
        match action:
            case 'STORE FILE':
                self._handle_store(argument)
            case 'STORE DIR':
                result = self._handle_store(argument, True)
                if result == -1:
                    response = 'Invalid Data'
            case _:
                response = 'Action Denied!'

        return response

    def _remove_tmp_file(self) -> None:
        if os.path.exists(self.tmp_file_path):
            os.remove(self.tmp_file_path)

    @classmethod
    def _handle_store(cls, save_path, directory=False) -> int:
        # add '/' to the beginning if necessary
        if save_path[0] != '/':
            save_path = '/' + save_path

        # create directories if they don't exist
        os.makedirs(cls.data_dir + save_path[:save_path.rindex('/')], exist_ok=True)

        print(f'\tSaving data to {save_path}')
        if not directory:
            shutil.move(cls.tmp_file_path, cls.data_dir + save_path)
            return 0

        # directories are send as compressed files
        if not zipfile.is_zipfile(cls.tmp_file_path):
            return -1
        with zipfile.ZipFile(cls.tmp_file_path, 'r') as zip_ref:
            zip_ref.extractall(cls.data_dir + save_path)

        return 0


class ServerActions:
    spacer = '<;;;>'
    end_transfer = '<;;EOT;;>'.encode()

    @classmethod
    def store_file(cls, file_path):
        return ('STORE FILE' + cls.spacer + file_path).encode()

    @classmethod
    def store_dir(cls, dir_path):
        return ('STORE DIR' + cls.spacer + dir_path).encode()

    @classmethod
    def retrieve(cls, data_path):
        raise NotImplementedError

    @classmethod
    def delete(cls, data_path):
        raise NotImplementedError

    @classmethod
    def synchronize(cls):
        raise NotImplementedError

    @classmethod
    def list_data(cls):
        raise NotImplementedError
