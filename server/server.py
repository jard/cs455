import re
class Channel():
    def __init__(self, name):
        self.name = name
        # keep track of the chatters on this channel
        self.chatters = {}

    def __str__(self):
        return str(self.name)

class Chatter():
    def __init__(self, socket, addr):
        self.username = None
        self.socket = socket
        self.addr = addr

    def pushMessage(self, msg):
        self.socket.send(msg)

class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # keep track of all the channels created on this server
        # store as dictionary so we can index by channel name
        self.channels = {}
        # keep track of all the clients who connect on this server
        # store as dictionary so we can index by username
        self.chatters = {}

    def username(self, chatter, username):
        res = None
        if username in self.chatters:
            res = "ERROR_ALREADY_REGISTERED\n"
        else:
            chatter.username = username
            self.chatters[username] = chatter
            res = "SUCCESS_WELCOME_TO_SERVER\n"
        chatter.pushMessage(res)

    def join(self, chatter, channel_name):
        res = None
        # need to make this match /^#[A-Za-z0-9_.@-]{1,64}$/
        if channel_name[0] != "#":
            res = "ERROR_INVALID_CHANNEL_NAME\n"
            chatter.pushMessage(res)
            return res

        if channel_name in self.channels:
            res = "SUCCESS_WELCOME_TO_CHANNEL\n"
            channel = self.channels[channel_name]
        else:
            res = "SUCCESS_NEW_CHANNEL_CREATED\n"
            channel = Channel(channel_name)
            self.channels[channel_name] = channel

        channel.chatters[chatter.username] = chatter
        chatter.pushMessage(res)
        return res

    def list(self, chatter, channels=None):
        channel_list = []
        # list all the channels
        if channels == None:
            for k in self.channels:
                channel_list.append(str(self.channels[k]))
        # list only the channels specified
        else:
            for k in channels:
                if k in self.channels:
                    channel_list.append(str(self.channels[k]))

        channel_list.append("") # for the terminating newline char
        res = "\n".join(channel_list)
        chatter.pushMessage(res)
        return res

    def part(self, chatter, channels=None):
        channel_list = []
        for k in channels:
            if k in self.channels and chatter.username in self.channels[k].chatters:
                del self.channels[k].chatters[chatter.username]
                channel_list.append("SUCCESS_PARTED_WITH_CHANNEL")
            elif k in self.channels:
                channel_list.append("ERROR_NOT_ON_CHANNEL")
            else:
                channel_list.append("ERROR_CHANNEL_DOES_NOT_EXIST")

        channel_list.append("") # for the terminating newline char
        res = "\n".join(channel_list)
        chatter.pushMessage(res)
        return res

    def privmsg(self, chatter, send_to, msg):
        # send to channel
        res = None
        if send_to[0] == "#":
            if send_to in self.channels:
                channel = self.channels[send_to]
                for username in channel.chatters:
                    self.chatters[username].pushMessage("PRIVMSG %s%s :%s\n" % (chatter.username, send_to, msg))
                res = "SUCCESS_MESSAGE_SENT_TO_CHANNEL\n"
            else:
                res = "ERROR_CHANNEL_DOES_NOT_EXIST\n"
        # send to user
        else:
            if send_to in self.chatters:
                self.chatters[send_to].pushMessage("PRIVMSG %s :%s\n" % (chatter.username, msg))
                res = "SUCCESS_MESSAGE_SENT_TO_USER\n"
            else:
                res = "ERROR_USER_DOES_NOT_EXIST\n"

        chatter.pushMessage(res)
        return res

