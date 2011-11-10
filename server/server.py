import re
import socket

SUCCESS_WELCOME_TO_SERVER = "SUCCESS_WELCOME_TO_SERVER\n"
SUCCESS_WELCOME_TO_CHANNEL = "SUCCESS_WELCOME_TO_CHANNEL\n"
SUCCESS_NEW_CHANNEL_CREATED = "SUCCESS_NEW_CHANNEL_CREATED\n"
SUCCESS_PARTED_WITH_CHANNEL = "SUCCESS_PARTED_WITH_CHANNEL\n"
SUCCESS_MESSAGE_SENT_TO_CHANNEL = "SUCCESS_MESSAGE_SENT_TO_CHANNEL\n"
SUCCESS_MESSAGE_SENT_TO_USER = "SUCCESS_MESSAGE_SENT_TO_USER\n"
SUCCESS_TOPIC_SET = "SUCCESS_TOPIC_SET\n"

ERROR_INVALID_USERNAME = "ERROR_INVALID_USERNAME\n"
ERROR_ALREADY_REGISTERED = "ERROR_ALREADY_REGISTERED\n"
ERROR_INVALID_CHANNEL_NAME = "ERROR_INVALID_CHANNEL_NAME\n"
ERROR_NOT_ON_CHANNEL = "ERROR_NOT_ON_CHANNEL\n"
ERROR_USER_DOES_NOT_EXIST = "ERROR_USER_DOES_NOT_EXIST\n"
ERROR_CHANNEL_DOES_NOT_EXIST = "ERROR_CHANNEL_DOES_NOT_EXIST\n"
ERROR_ALREADY_ON_CHANNEL = "ERROR_ALREADY_ON_CHANNEL\n"
ERROR_USERNAME_REQUIRED = "ERROR_USERNAME_REQUIRED\n"
ERROR_NEED_MORE_PARAMS = "ERROR_NEED_MORE_PARAMS\n"
ERROR_INVALID_COMMAND  = "ERROR_INVALID_COMMAND\n"
ERROR_CANNOT_CHANGE_USERNAME = "ERROR_CANNOT_CHANGE_USERNAME\n"
ERROR_CANNOT_SET_CHANNEL_TOPIC = "ERROR_CANNOT_SET_CHANNEL_TOPIC\n"


class Channel():
    def __init__(self, name, owner, topic=""):
        self.name = name
        self.topic = topic
        self.owner = owner
        # keep track of the clients on this channel using a dictionary (where
        # the key is their username)
        self.clients = {}

    def __str__(self):
        return str(self.name + " " + self.owner.username + " :" + self.topic)

    def partWithClient(self, client):
        try:
            del self.clients[client.username]
        except KeyError, e:
            pass # client already left channel
        return len(self.clients)

class Client():
    def __init__(self, socket, addr):
        # a client doesn't have a username until they request one from the
        # server
        self.username = None
        self.socket = socket
        self.addr = addr

    # send out a message to the client through the socket
    def pushMessage(self, msg):
        try:
            bytes_sent = self.socket.send(msg)
            if bytes_sent == len(msg):
                return msg
        except socket.error, e:
            pass 

        # the user probably already left (and hasn't been removed yet)
        return False

    # close TCP connection
    def quit(self):
        self.socket.close()

class Server():
    COMMAND_META = {"USER":    {'params': 1, 'username_required': False},
                    "PRIVMSG": {'params': 2, 'username_required': True},
                    "JOIN":    {'params': 1, 'username_required': True},
                    "TOPIC":   {'params': 2, 'username_required': True},
                    "LIST":    {'params': 0, 'username_required': True},
                    "PART":    {'params': 1, 'username_required': True},
                    "QUIT":    {'params': 0, 'username_required': False}}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        # keep track of all the channels created on this server
        # store as dictionary so we can index by channel name
        self.channels = {}
        # keep track of all the clients who connect on this server
        # store as dictionary so we can index by username
        self.clients = {}

    def handleCommand(self, client, cmd, args):
        # valid command?
        if cmd not in Server.COMMAND_META:
            return client.pushMessage(ERROR_INVALID_COMMAND)
            
        meta = Server.COMMAND_META[cmd]
        # need username?
        if not client.username and meta['username_required']:
            return client.pushMessage(ERROR_USERNAME_REQUIRED)
        # need more params?
        if len(args) < meta['params']:
            return client.pushMessage(ERROR_NEED_MORE_PARAMS)

        # clear to issue command
        if cmd == "USER":
            msg = self.user(client, args[0])
        elif cmd == "PRIVMSG":
            msg = self.privmsg(client, args[0], args[1])
        elif cmd == "JOIN":
            msg = self.join(client, args)
        elif cmd == "TOPIC":
            msg = self.topic(client, args[0], args[1])
        elif cmd == "LIST":
            msg = self.list(client, args)
        elif cmd == "PART":
            msg = self.part(client, args)
        elif cmd == "QUIT":
            msg = self.quit(client, args[0] if args else "")

        return msg

    # sets the username of client (if it is available)
    def user(self, client, username):
        if client.username:
            res = ERROR_CANNOT_CHANGE_USERNAME
        if not self.isValidUsername(username):
            res = ERROR_INVALID_USERNAME
        elif username in self.clients:
            res = ERROR_ALREADY_REGISTERED
        else:
            client.username = username
            self.clients[username] = client
            res = SUCCESS_WELCOME_TO_SERVER
        client.pushMessage(res)
        return res

    # join the channel or channels specified (by their name) 
    def join(self, client, channels):
        # since multiple channels can be specified, we need to keep track of
        # all the response messages for each channel
        total_res = [] 

        # for each channel, check if it exists, and join it
        for channel_name in channels:
            # bad channel name
            if not self.isValidChannelName(channel_name):
                res = ERROR_INVALID_CHANNEL_NAME
            # valid channel name
            else:
                # they are joining an already existing channel
                if channel_name in self.channels:
                    channel = self.channels[channel_name]
                    if client.username in channel.clients:
                        res = ERROR_ALREADY_ON_CHANNEL
                    else:
                        res = SUCCESS_WELCOME_TO_CHANNEL
                # they are creating a new channel
                else:
                    res = SUCCESS_NEW_CHANNEL_CREATED
                    channel = Channel(channel_name, client)

                # add to our list of channels
                self.channels[channel_name] = channel
                # add the user to the channel
                channel.clients[client.username] = client
            # tack on the response message for this channel
            total_res.append(res)

        # all done, send the big response to the client
        res = "".join(total_res)
        client.pushMessage(res)
        return res

    def topic(self, client, channel, topic):
        res = None
        if channel not in self.channels:
            res = ERROR_CHANNEL_DOES_NOT_EXIST
        elif self.channels[channel].owner != client:
            res = ERROR_CANNOT_SET_CHANNEL_TOPIC
        else:
            self.channels[channel].topic = topic
            res = SUCCESS_TOPIC_SET

        client.pushMessage(res)
        return res

    # list all the channels on the server, or just the ones specified
    def list(self, client, channels):
        channel_list = []

        if channels:
            # list only the channels specified
            for k in channels:
                # only add it to the response if it actually exists
                if k in self.channels:
                    channel_list.append(str(self.channels[k]))
        else:
            # list all the channels
            for k in self.channels:
                channel_list.append(str(self.channels[k]))

        # all done, send the big response back to the client
        channel_list.append("") # for the terminating newline char
        res = "\n".join(channel_list)
        client.pushMessage(res)
        return res

    # leave a channel
    def part(self, client, channels):
        # keep track of all the response messages for every channel you are
        # leaving
        channel_list = []
        for k in channels:
            # only remove the user from the channel if they're on it
            if k in self.channels and client.username in self.channels[k].clients:
                # remove the client from the channel
                self.removeClientFromChannel(client, self.channels[k])
                channel_list.append(SUCCESS_PARTED_WITH_CHANNEL)
            elif k in self.channels:
                channel_list.append(ERROR_NOT_ON_CHANNEL)
            else:
                channel_list.append(ERROR_CHANNEL_DOES_NOT_EXIST)

        # send the big response message back to client
        res = "".join(channel_list)
        client.pushMessage(res)
        return res

    # send a message to a user or entire channel
    def privmsg(self, client, send_to, msg):
        # send to channel
        if send_to[0] == "#":
            # does the channel actually exist?
            if send_to in self.channels:
                channel = self.channels[send_to]
                # send the message to every user on the channel
                for username in channel.clients:
                    self.clients[username].pushMessage("PRIVMSG %s%s :%s\n" % (client.username, send_to, msg))
                res = SUCCESS_MESSAGE_SENT_TO_CHANNEL
            # bad channel name
            else:
                res = ERROR_CHANNEL_DOES_NOT_EXIST
        # send to user
        else:
            # does the user actually exist?
            if send_to in self.clients:
                # send the message to the user specified
                self.clients[send_to].pushMessage("PRIVMSG %s :%s\n" % (client.username, msg))
                res = SUCCESS_MESSAGE_SENT_TO_USER
            else:
                res = ERROR_USER_DOES_NOT_EXIST

        client.pushMessage(res)
        return res

    # remove the user from the server
    def quit(self, client, message):
        # remove the user from all the channels they are in
        for channel_name in self.channels.keys():
            self.removeClientFromChannel(client, self.channels[channel_name])

        quitter_username = client.username
        msg = "QUIT"
        # only send quit message if they have a username
        if quitter_username:
            # now delete client from server
            del self.clients[client.username]
            client.quit()

            # broadcast message to everyone else
            msg = "QUIT " + quitter_username  + " :" + message + "\n"
            for username, client in self.clients.items():
                client.pushMessage(msg)

        return msg

    # close the server 
    def squit(self, message):
        msg = "SQUIT :" + message + "\n"
        for username, client in self.clients.items():
            client.pushMessage(msg)
            client.quit()

        return msg

    ###########
    # helpers #
    ###########

    # removes the user from the channel, and delete the channel if no one is in
    # it anymore
    def removeClientFromChannel(self, client, channel):
        clients_remaining = channel.partWithClient(client)
        if clients_remaining == 0:
            del self.channels[channel.name]

    def isValidChannelName(self, name):
        return not re.match(r'^#[A-Za-z0-9_.@-]{1,64}$', name) == None

    def isValidUsername(self, name):
        return not re.match(r'^[A-Za-z0-9_.@-]{1,64}$', name) == None
