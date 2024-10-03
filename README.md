# Python Backup App

Implementacja systemu do synchronizacji i backupu danych multimedialnych z wykorzystaniem protokołów sieciowych
  
Zadania:
-	Badanie protokołów sieciowych do synchronizacji i backupu.
-	Zaprojektowanie architektury systemu.
-	Implementacja funkcji synchronizacji danych.
-	Implementacja funkcji backupu danych.
-	Testowanie systemu pod kątem niezawodności.
-	Opracowanie dokumentacji technicznej.


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

### Running app with docker-compose
```shell
docker-compose -f docker-compose.yml up
```
