import sys
import re
import thread
import socket
import server


# returns a 2-tuple containing the command message, and its arguments
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
        return data[0], None

    return data[0], data[1:]

def handler(client_socket, client_addr, serv):
    client = server.Chatter(client_socket, client_addr)
    print "Accepted connection from: ", client.addr
    while 1:
        data = client_socket.recv(1024)
        cmd, args = parseCommandMessage(data)
        msg = None

        if cmd == "USER":
            msg = serv.username(client, args[0])
        elif cmd == "PRIVMSG":
            msg = serv.privmsg(client, args[0], args[1])
        elif cmd == "JOIN":
            msg = serv.join(client, args)
        elif cmd == "LIST":
            msg = serv.list(client, args)
        elif cmd == "PART":
            msg = serv.part(client, args)
        else:
            msg = "ERROR_INVALID_COMMAND\n"

        if msg != None:
            print msg

    client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        port = 5000
    else:
        port = int(sys.argv[1])

    #host = socket.gethostbyname(socket.gethostname())
    host = 'localhost'
    buf = 1024
    addr = (host, port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(addr)
    server_socket.listen(2)
    serv = server.Server(host, port)

    while 1:
        print "Server is listening for connections\n"
        client_socket, client_addr = server_socket.accept()
        thread.start_new_thread(handler, (client_socket, client_addr, serv))
    server_socket.close()
