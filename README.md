# Python Backup App

Implementacja systemu do synchronizacji i backupu danych multimedialnych z wykorzystaniem protokołów sieciowych
  
Zadania:
-	Badanie protokołów sieciowych do synchronizacji i backupu.
-	Zaprojektowanie architektury systemu.
-	Implementacja funkcji synchronizacji danych.
-	Implementacja funkcji backupu danych.
-	Testowanie systemu pod kątem niezawodności.
-	Opracowanie dokumentacji technicznej.

## Running Server
```shell
python server.py
```

## FIXME: Sending data from client to server
```shell
python backapp.py
```

## Self-signed SSL certificate with `openssl`
Generate a 2048-bit RSA private key:
```shell
openssl genrsa -out ./certificates/py-backapp-server.key 2048
```
Generate a certificate signing request:
```shell
openssl req -new -key ./certificates/py-backapp-server.key -out ./certificates/py-backapp-server.csr
```
Generate self-signed certificate, valid for 365 days:
```shell
openssl x509 -req -days 365 -in ./certificates/py-backapp-server.csr -signkey ./certificates/py-backapp-server.key -out ./certificates/py-backapp-server.crt
```
Verify certificate and key:
```shell
openssl x509 -in ./certificates/py-backapp-server.crt -noout -text
openssl rsa -in ./certificates/py-backapp-server.key -noout -text
```

## Docker

### Building image
```shell
docker image build -f server.Dockerfile -t py-backapp:test .
```
### Running container
```shell
docker container run py-backapp:test
```
### Running bash in a container
```shell
docker container run -it py-backapp:test "/bin/bash"
```

### Running with docker-compose
```shell
docker-compose -f docker-compose.yml up
```
\
\
![docker example 1](/screenshots/docker_1.png)
