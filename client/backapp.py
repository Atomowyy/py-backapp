from tcp_client import TcpClient

from datetime import datetime
import os

client = TcpClient()

#####################################
# client.get_auth_token()  # 0 - token received, 1 - error
#####################################
token_is_valid = (client.verify_token() == 0)  # 0 - valid, 1 - invalid

if not token_is_valid:
    raise Exception("Invalid token")
#####################################

response = client.store('../LICENSE', 'test/test2/')  # file transfer
# response = client.store('../screenshots', 'test/folder')  # dir transfer

# response = client.get('/test/test2/LICENSE', './')  # get file
# response = client.get('/test', './', True)  # get dir

# ls, response = client.list_data('/test/folder/screenshots')  # list data
# print(ls)

# print(f'local modification date: {datetime.fromtimestamp(os.path.getmtime("../screenshots/docker_1.png"))}')
# mod_date, response = client.get_modification_date('/test/folder/screenshots/docker_1.png')  # get modification date
# print(mod_date)

# response = client.delete('/')  # delete all data on the server

print(response)
