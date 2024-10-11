from tcp_server import TcpServer
import os

PORT = int(os.getenv('PORT', 1234))
BACKLOG = int(os.getenv('BACKLOG', 0))
TCP_BUFFER_SIZE = int(os.getenv('TCP_BUFFER_SIZE', 32_768))

# FIXME: use your certificates, default certificates are for development purposes only and shouldn't be used
CERTFILE = os.getenv('CERTFILE', 'certificates/py-backapp-development.crt')
KEYFILE = os.getenv('KEYFILE', 'certificates/py-backapp-development.key')

try:
    # initialize server
    server = TcpServer(CERTFILE, KEYFILE, PORT, BACKLOG, TCP_BUFFER_SIZE)

    # run the server
    server.run()
except KeyboardInterrupt:  # catch keyboard interrupts, mainly Ctrl+C
    print("\nStopping server...")
