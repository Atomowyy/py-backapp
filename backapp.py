import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server
client_socket.connect(('localhost', 1234))

try:
    message = 'Hello There 12345!'
    client_socket.sendall(message.encode())

except socket.error as err:
    print(f'Socket error: {err}')

finally:
    client_socket.close()