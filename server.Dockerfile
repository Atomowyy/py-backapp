FROM python:3.12-bookworm

WORKDIR /py-backapp-server

ENV PYTHONUNBUFFERED=1 \
    PORT=1234 \
    BACKLOG=0 \
    TCP_BUFFER_SIZE=32768 \
    CERTFILE='certificates/py-backapp-development.crt' \
    KEYFILE='certificates/py-backapp-development.key'

EXPOSE $PORT/tcp

COPY ./certificates ./certificates
COPY ./TcpServer.py .
COPY ./server.py .

CMD [ "python3", "./server.py" ]