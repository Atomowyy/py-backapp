import socket
import ssl

from server.tcp_server import ServerActions

# create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# create ssl context
context = ssl.create_default_context()

# disable certificate verification (required for self-signed certificates to work properly)
# FIXME:
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# wrap client socket with ssl
secure_socket = context.wrap_socket(client_socket, server_hostname='localhost')

# connect to server
secure_socket.connect(('localhost', 1234))

try:
    command = ServerActions.store('/dir1/dir2/file.txt')
    secure_socket.sendall(command)  # sendall - wait until all data is sent, else error

    data = 'Hello There 12345!'.encode()
    secure_socket.sendall(data)

except socket.error as err:
    print(f'Socket error: {err}')

finally:
    secure_socket.close()
