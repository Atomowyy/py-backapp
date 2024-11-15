# Python Backup App

## Projekt:
Implementacja systemu do synchronizacji i backupu danych multimedialnych z wykorzystaniem protokołów sieciowych

Zadania:
-	Badanie protokołów sieciowych do synchronizacji i backupu.
-	Zaprojektowanie architektury systemu.
-	Implementacja funkcji synchronizacji danych.
-	Implementacja funkcji backupu danych.
-	Testowanie systemu pod kątem niezawodności.
-	Opracowanie dokumentacji technicznej.

## Cloning repo
```shell
git clone https://github.com/Atomowyy/py-backapp && cd py-backapp
```

## Running Client
> [!NOTE]
> Change directory to `client`

### Interactive mode
Run with no arguments or with `-i` flag to start interactive mode
```text
python backapp.py
```
```text
python backapp.py -i
```
![image](https://github.com/user-attachments/assets/92ef0ac6-4e80-4ded-b98a-9b9b893bdddd)


### CLI mode
```text
python backapp.py -h
```
```text
usage: backapp.py [-h] [-i] [--username USERNAME] [--server SERVER] [--port PORT] [-g] [-v] [--local LOCAL]
                  [--remote REMOTE] [-l] [-r] [-R] [-u] [-d] [-s] [-S]

This is the client side of py-backapp, backup and synchronize your files with the server.If no argument is
specified the program starts in interactive mode

options:
  -h, --help           show this help message and exit
  -i, --interactive    start py-backapp in interactive mode
  --username USERNAME  set username in config.json
  --server SERVER      set server in config.json
  --port PORT          set port in config.json
  -g, --gettoken       authorize user on the server and get a token
  -v, --verifytoken    verify if current token is valid
  --local LOCAL        path to local resource
  --remote REMOTE      path to remote resource
  -l, --list           list contents of remote dir
  -r, --remove         remove remote resources
  -R, --removeall      remove all users' remote resources
  -u, --upload         upload local resources to the server
  -d, --download       download remote resources from the server
  -s, --syncfile       compare local and remote file and get the newer one
  -S, --syncdir        synchronize local directory with the remote one

source code: https://github.com/Atomowyy/py-backapp
```
![image](https://github.com/user-attachments/assets/c9719a2a-24ab-4f2e-9063-4dba35679c30)
![image](https://github.com/user-attachments/assets/2c436d24-fad8-409e-b953-39fb93342aad)
![image](https://github.com/user-attachments/assets/7e783a12-7ba1-4af7-8830-496216be6d2a)



## Running Server
> [!NOTE]
> Change directory to `server`

```shell
python server.py
```
![image](https://github.com/user-attachments/assets/31a38b17-e7d7-4f80-aae7-264b2faeec30)


## Adding users to servers' database
> [!NOTE]
> Change directory to `server`

Users are stored in `users_db.json`
```shell
python users_db_add_user.py
```
![image](https://github.com/user-attachments/assets/3932d217-707d-42fd-9ec7-dd6e4b571568)
![image](https://github.com/user-attachments/assets/42641cd9-3fdb-4932-a205-b8983e4f1f92)


## Self-signed SSL certificate with `openssl`
Generate a 2048-bit RSA private key:
```shell
openssl genrsa -out ./server/certificates/py-backapp-server.key 2048
```
Generate a certificate signing request:
```shell
openssl req -new -key ./server/certificates/py-backapp-server.key -out ./certificates/py-backapp-server.csr
```
Generate self-signed certificate, valid for 365 days:
```shell
openssl x509 -req -days 365 -in ./server/certificates/py-backapp-server.csr -signkey ./certificates/py-backapp-server.key -out ./certificates/py-backapp-server.crt
```
Verify certificate and key:
```shell
openssl x509 -in ./server/certificates/py-backapp-server.crt -noout -text
openssl rsa -in ./server/certificates/py-backapp-server.key -noout -text
```
\
\
Modify ceritficates in `server.py` or set the env variables
```python
# FIXME: use your certificates, default certificates are for development purposes only and shouldn't be used
CERTFILE = os.getenv('CERTFILE', 'certificates/py-backapp-server.crt')
KEYFILE = os.getenv('KEYFILE', 'certificates/py-backapp-server.key')
```
```shell
export CERTFILE=certificates/py-backapp-server.crt
export KEYFILE=certificates/py-backapp-server.key
```

## Docker

### Building server image
```shell
docker image build -f ./server/server.Dockerfile -t py-backapp:test .
```
### Running server in a container
```shell
docker container run -p 1234:1234 py-backapp:test
```
### Running bash in a server container
```shell
docker container run -it -p 1234:1234 py-backapp:test /bin/bash
```

### Running server with docker-compose
```shell
docker-compose -f docker-compose.yml up
```
\
\
![image](https://github.com/user-attachments/assets/9085b9fa-8419-4f76-95ff-2bfdb8a34ccc)
![image](https://github.com/user-attachments/assets/b947e931-93c7-452c-aef4-538d56734700)


