import socket
import ssl

import zipfile

from server.tcp_server import ServerActions

import os
import shutil

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
command = ServerActions.store_file('test/test2/file.txt')
secure_socket.sendall(command)  # sendall - wait until all data is sent, else error

data = 'Hello There 12345!'.encode()
secure_socket.sendall(data)
secure_socket.sendall(ServerActions.end_transfer)

# get server response
response = secure_socket.recv(1024)
print(response.decode())

#####################################
# print('\nTesting folder transfer')
# command = ServerActions.store_dir('test/folder')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
#
# zip_path = shutil.make_archive('test', 'zip', '../screenshots')  # zip screenshots folder
# with open(zip_path, 'rb') as f:
#     data = f.read()
#
# os.remove(zip_path)
#
# secure_socket.sendall(data)
# secure_socket.sendall(ServerActions.end_transfer)
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting listing')
# command = ServerActions.list_data('/test/folder')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
# secure_socket.sendall(ServerActions.end_transfer)
#
# # get server response - listing of files
# ls = secure_socket.recv(1024)
# print(ls.decode())
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting Deleting')
# command = ServerActions.delete('/')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
# secure_socket.sendall(ServerActions.end_transfer)
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting file retrieving')
# command = ServerActions.get_file('/test/test2/file.txt')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
# secure_socket.sendall(ServerActions.end_transfer)
#
# file = 'retrieved_text.txt'
# with open(file, 'w') as f:  # clear file
#     pass
#
# while True:
#     # receive data
#     data = secure_socket.recv(1024)
#     if not data or data == ServerActions.end_transfer:
#         break
#
#     # store data in tmp file
#     with open(file, 'ab') as tmp_file:
#         tmp_file.write(data)
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())

#####################################
# print('\nTesting directory retrieving')
# command = ServerActions.get_dir('/test')
# secure_socket.sendall(command)  # sendall - wait until all data is sent, else error
# secure_socket.sendall(ServerActions.end_transfer)
#
# file = 'retrieved_directory.zip'
# with open(file, 'w') as f:  # clear file
#     pass
#
# while True:
#     # receive data
#     data = secure_socket.recv(1024)
#     if not data or data == ServerActions.end_transfer:
#         break
#
#     # store data in tmp file
#     with open(file, 'ab') as tmp_file:
#         tmp_file.write(data)
#
# # unzip the directory
# if not zipfile.is_zipfile(file):
#     raise Exception('Not a zip file')
# with zipfile.ZipFile(file, 'r') as zip_ref:
#     zip_ref.extractall('./')
#
# # rm .zip file
# os.remove(file)
#
# # get server response
# response = secure_socket.recv(1024)
# print(response.decode())
