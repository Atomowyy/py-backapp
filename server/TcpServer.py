import socket
import ssl

import os


class TcpServer:
    @classmethod
    def get_host_ip(cls):
        return socket.gethostbyname(socket.gethostname())

    def __init__(self, certfile, keyfile, port=1234, backlog=0, tcp_buffer_size=32_768):
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

    def run(self):
        # create server socket
        # AF_INET - IPv4, SOCK_STREAM - TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind socket to all available ipv4 interfaces and PORT
        self.server_socket.bind(('', self.port))

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
            try:
                client_socket, client_address = self.server_socket.accept()
                self.handle_connection(client_socket, client_address)
            except socket.error as err:
                print(f'Socket error: {err}')

    def handle_connection(self, client_socket, client_address):
        # secure client socket with ssl
        secure_socket = self.context.wrap_socket(client_socket, server_side=True)

        # print connection info
        print(f'Accepted connection from {client_address[0]}:{client_address[1]}, TLS version: {secure_socket.version()}')

        try:
            # receive data
            while True:
                data = secure_socket.recv(self.tcp_buffer_size)

                if data:
                    print(f'Received: {data.decode()}')
                else:
                    break

        except socket.error as err:
            print(f'Socket error: {err}')

        finally:
            secure_socket.close()
