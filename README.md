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

## FIXME: Sending data from client to server
```shell
python backapp.py
```

## Running Server
> [!NOTE]
> Change directory to `server`

```shell
python server.py
```

## Adding users to servers' database
```shell
python server/users_db_add_user.py
```

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
docker container run --rm -it -p 1234:1234 py-backapp:test "/bin/bash"
```

### Running server with docker-compose
```shell
docker-compose -f docker-compose.yml up
```
\
\
![docker example 1](/screenshots/docker_1.png)
