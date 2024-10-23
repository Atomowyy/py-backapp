import socket
import ssl

import tarfile

from server.tcp_server import ServerActions

import os
from datetime import datetime


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


#####################################
print('\nTesting file transfer')
command = ServerActions.store('test/test2/')
secure_socket.sendall(command)  # sendall - wait until all data is sent, else error

path = '../LICENSE'
socket_file = secure_socket.makefile('wb')
with tarfile.open(fileobj=socket_file, mode='w|') as socket_tar:
    socket_tar.add(path, arcname=os.path.basename(path))

# get server response
response = secure_socket.recv(1024)
print(response.decode())

#####################################
# print('\nTesting folder transfer')
# command = ServerActions.store('test/folder')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# path = '../screenshots'  # send directory
# # path = '../screenshots/'  # send only contents of directory
# with tarfile.open(fileobj=secure_socket.makefile('wb'), mode='w|') as tar:
#     tar.add(path, arcname=os.path.basename(path))
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting listing')
# command = ServerActions.list_data('/test/folder/screenshots')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# # get server response - listing of files
# ls = secure_socket.recv(1024)
# print(ls.decode())
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting getting modification date')
# command = ServerActions.get_modification_date('/test/folder/screenshots/docker_1.png')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# # print local modification date
# print(f'modification date: {datetime.fromtimestamp(os.path.getmtime("../screenshots/docker_1.png"))}')
#
# # get modification date
# response = secure_socket.recv(1024)
# modification_date = datetime.fromisoformat(response.decode())
# print(f'Modification date on server: {modification_date}')
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting Deleting')
# command = ServerActions.delete('/')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting file retrieving')
# command = ServerActions.get_file('/test/test2/LICENSE')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# # get and extract tar archive
# socket_file = secure_socket.makefile('rb')
# with tarfile.open(fileobj=socket_file, mode='r|') as tar:
#     tar.extractall('./', filter='tar')
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting directory retrieving')
# command = ServerActions.get_dir('/test')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# # get and extract tar archive
# socket_file = secure_socket.makefile('rb')
#
# with tarfile.open(fileobj=socket_file, mode='r|') as tar:
#     tar.extractall('./', filter='tar')
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())
