import socket

class TcpServer:
    @classmethod
    def get_host_ip(cls):
        return socket.gethostbyname(socket.gethostname())

    def __init__(self, port, backlog, tcp_buffer_size):
        self.port = port
        self.backlog = backlog
        self.tcp_buffer_size = tcp_buffer_size
        self.server_socket = None

    def run(self):
        # create server socket
        # AF_INET - IPv4, SOCK_STREAM - TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind socket to all available ipv4 interfaces and PORT
        self.server_socket.bind(('', self.port))

        # start listening and set backlog
        self.server_socket.listen(self.backlog)

        # waiting for connections
        print(f'Started py-backapp server on {self.get_host_ip()}:{self.port}')
        while True:
            try:
                connection, client_address = self.server_socket.accept()
                print(f'Accepted connection from {client_address[0]}:{client_address[1]}')
                self.handle_connection(connection)
            except socket.error as err:
                print(f'Socket error: {err}')

    def handle_connection(self, connection):
        try:
            # receive data
            while True:
                data = connection.recv(self.tcp_buffer_size)

                if data:
                    print(f'Received: {data.decode()}')
                else:
                    break

        except socket.error as err:
            print(f'Socket error: {err}')

        finally:
            connection.close()
