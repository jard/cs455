import sys
import re
import thread
import socket
from server import Server, Client

DEFAULT_PORT = 5000
DEFAULT_HOST = 'localhost'
BUFFER_SIZE = 1024

# returns a 2-tuple containing the command message, and its arguments
# if there are no arguments, args is set to the empty array
def parseCommandMessage(data):
    data = data.strip() # remove newline
    position_of_colon = data.find(":")

    if position_of_colon == -1:
        # simple command
        data = re.split(r' ', data)
    else:
        # complex command 
        # grab the stuff upto the colon (which is separated by spaces)
        first_part = re.split(r' ', data[:position_of_colon-1])
        # add on the stuff after the colon
        first_part.append(data[position_of_colon+1:])
        data = first_part

    if len(data) == 1:
        return data[0], []

    return data[0], data[1:]

# when a client connects, this function gets excuted on the newly created
# thread
def onClientConnected(client_socket, client_addr, server):
    client = Client(client_socket, client_addr)
    print "Accepted connection from: ", client.addr
    # wait for something to come from the socket
    while 1:
        # get and parse the command from the socket
        data = client_socket.recv(BUFFER_SIZE)
        if data == "":
            break

        cmd, args = parseCommandMessage(data)
        msg = server.handleCommand(client, cmd, args)

        # quit command was issued
        if msg == False:
            break

        # this is the message that was sent to the client (print it on the
        # server for debugging purposes)
        print msg


    # client killed connection rudely, so we need to issue quit command
    if data == "":
        print "Rudely closed connection"
        server.quit(client, "")

    print "Closed connection from ", client.addr

if __name__ == "__main__":
    #host = socket.gethostbyname(socket.gethostname())
    if len(sys.argv) != 2:
        port = DEFAULT_PORT
    else:
        port = int(sys.argv[1])

    # setup the server socket
    host = DEFAULT_HOST
    addr = (host, port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(addr)
    server_socket.listen(2)

    # create our little server
    server = Server(host, port)

    # wait for connections
    try:
        while 1:
            print "Server is listening for connections on %s:%s\n" % (host, port)
            # spawn off a new thread for this connection
            client_socket, client_addr = server_socket.accept()
            thread.start_new_thread(onClientConnected, (client_socket, client_addr, server))
    except KeyboardInterrupt:
        server.squit("I was killed by a ^C")

    server_socket.close()
