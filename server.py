from TcpServer import TcpServer

PORT = 1234
BACKLOG = 0  # number of allowed connections in the queue
TCP_BUFFER_SIZE = 32_768  # buffer size in bytes, max = 65_536

try:
    # initialize server
    server = TcpServer(PORT, BACKLOG, TCP_BUFFER_SIZE)

    # run the server
    server.run()
except KeyboardInterrupt:  # catch keyboard interrupts, mainly Ctrl+C
    print("\nStopping server...")