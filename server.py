import sys
import re
import thread
import socket

# holds the sockets for everyone who connects AND issues a USER command
# the index is the username
connections = {}

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
    return data[0], data[1:]

def handler(client_socket, client_addr):
    print "Accepted connection from: ", client_addr
    username = None
    while 1:
        data = client_socket.recv(1024)
        cmd, args = parseCommandMessage(data)
        msg = None

        if cmd == "USER":
            requested_username = args[0]
            # need a mutex here
            # Username is available
            if requested_username not in connections:
                username = requested_username
                connections[username] = client_socket
                msg = "SUCCESS_WELCOME_TO_SERVER\n"
            # Username is not available
            else:
                msg = "ERROR_ALREADY_REGISTERED\n"
        elif cmd == "PRIVMSG":
            send_to = args[0]
            # need another mutex here
            if send_to not in connections:
                msg = "ERROR_USER_DOES_NOT_EXIST\n"
            else:
                message_to_user = args[1] + "\n"
                try:
                    bytes_sent = connections[send_to].send(message_to_user)
                    if bytes_sent != len(message_to_user):
                        msg = "ERROR_MESSAGE_NOT_SENT_FOR_UNKNOWN_REASON\n"
                except socket.error, e:
                    # connection doesn't exist anymore
                    del connections[send_to]
                    msg = "ERROR_USER_NOT_CONNECTED\n"
        else:
            msg = "ERROR_INVALID_COMMAND\n"

        if msg != None:
            try:
                client_socket.send(msg)
            except socket.error, e:
                # remove the connection if it still exists
                if username in connections:
                    del connections[username]
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

    while 1:
        print "Server is listening for connections\n"
        client_socket, client_addr = server_socket.accept()
        thread.start_new_thread(handler, (client_socket, client_addr))
    server_socket.close()
