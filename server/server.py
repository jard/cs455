import re
import socket
class Channel():
    def __init__(self, name, topic=""):
        self.name = name
        self.topic = topic
        # keep track of the chatters on this channel using a dictionary (where
        # the key is their username)
        self.chatters = {}

    def __str__(self):
        return str(self.name + " " + self.topic)

    def partWithChatter(self, chatter):
        try:
            del self.chatters[chatter.username]
        except KeyError, e:
            pass # chatter already left channel
        return len(self.chatters)

class Chatter():
    def __init__(self, socket, addr):
        # a chatter doesn't have a username until they request one from the
        # server
        self.username = None
        self.socket = socket
        self.addr = addr

    # send out a message to the client through the socket
    def pushMessage(self, msg):
        try:
            bytes_sent = self.socket.send(msg)
            if bytes_sent == len(msg):
                return True
        except socket.error, e:
            pass 

        # the user probably already left (and hasn't been removed yet)
        return False

    # close TCP connection
    def quit(self):
        self.socket.close()

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

    # sets the username of chatter (if it is available)
    def user(self, chatter, username):
        if not self.isValidUsername(username):
            res = "ERROR_INVALID_USERNAME\n"
        elif username in self.chatters:
            res = "ERROR_ALREADY_REGISTERED\n"
        else:
            chatter.username = username
            self.chatters[username] = chatter
            res = "SUCCESS_WELCOME_TO_SERVER\n"
        chatter.pushMessage(res)
        return res

    # join the channel or channels specified (by their name) 
    def join(self, chatter, channels):
        # since multiple channels can be specified, we need to keep track of
        # all the response messages for each channel
        total_res = [] 

        # for each channel, check if it exists, and join it
        for channel_name in channels:
            # bad channel name
            if not self.isValidChannelName(channel_name):
                res = "ERROR_INVALID_CHANNEL_NAME"
            # valid channel name
            else:
                # they are joining an already existing channel
                if channel_name in self.channels:
                    res = "SUCCESS_WELCOME_TO_CHANNEL"
                    channel = self.channels[channel_name]
                # they are creating a new channel
                else:
                    res = "SUCCESS_NEW_CHANNEL_CREATED"
                    channel = Channel(channel_name)

                # add to our list of channels
                self.channels[channel_name] = channel
                # add the user to the channel
                channel.chatters[chatter.username] = chatter
            # tack on the response message for this channel
            total_res.append(res)

        # all done, send the big response to the client
        total_res.append("") # for the ending newline
        res = "\n".join(total_res)
        chatter.pushMessage(res)
        return res

    # list all the channels on the server, or just the ones specified
    def list(self, chatter, channels):
        channel_list = []
        # list only the channels specified
        for k in channels:
            # only add it to the response if it actually exists
            if k in self.channels:
                channel_list.append(str(self.channels[k]))
        # list all the channels
        else:
            for k in self.channels:
                channel_list.append(str(self.channels[k]))

        # all done, send the big response back to the client
        channel_list.append("") # for the terminating newline char
        res = "\n".join(channel_list)
        chatter.pushMessage(res)
        return res

    # leave a channel
    def part(self, chatter, channels):
        # keep track of all the response messages for every channel you are
        # leaving
        channel_list = []
        for k in channels:
            # only remove the user from the channel if they're on it
            if k in self.channels and chatter.username in self.channels[k].chatters:
                # remove the chatter from the channel
                self.removeChatterFromChannel(chatter, self.channels[k])
                channel_list.append("SUCCESS_PARTED_WITH_CHANNEL")
            elif k in self.channels:
                channel_list.append("ERROR_NOT_ON_CHANNEL")
            else:
                channel_list.append("ERROR_CHANNEL_DOES_NOT_EXIST")

        # send the big response message back to client
        channel_list.append("") # for the terminating newline char
        res = "\n".join(channel_list)
        chatter.pushMessage(res)
        return res

    # send a message to a user or entire channel
    def privmsg(self, chatter, send_to, msg):
        # send to channel
        if send_to[0] == "#":
            # does the channel actually exist?
            if send_to in self.channels:
                channel = self.channels[send_to]
                # send the message to every user on the channel
                for username in channel.chatters:
                    self.chatters[username].pushMessage("PRIVMSG %s%s :%s\n" % (chatter.username, send_to, msg))
                res = "SUCCESS_MESSAGE_SENT_TO_CHANNEL\n"
            # bad channel name
            else:
                res = "ERROR_CHANNEL_DOES_NOT_EXIST\n"
        # send to user
        else:
            # does the user actually exist?
            if send_to in self.chatters:
                # send the message to the user specified
                self.chatters[send_to].pushMessage("PRIVMSG %s :%s\n" % (chatter.username, msg))
                res = "SUCCESS_MESSAGE_SENT_TO_USER\n"
            else:
                res = "ERROR_USER_DOES_NOT_EXIST\n"

        chatter.pushMessage(res)
        return res

    # remove the user from the server
    def quit(self, chatter, message):
        # remove the user from all the channels they are in
        for channel_name in self.channels.keys():
            self.removeChatterFromChannel(chatter, self.channels[channel_name])

        quitter_username = chatter.username
        msg = None
        # only send quit message if they have a username
        if quitter_username:
            # now delete chatter from server
            del self.chatters[chatter.username]
            chatter.quit()

            # broadcast message to everyone else
            msg = "QUIT " + quitter_username  + " :" + message + "\n"
            for username, chatter in self.chatters.items():
                chatter.pushMessage(msg)

        return msg

    # close the server 
    def squit(self, message):
        msg = "SQUIT :" + message + "\n"
        for username, chatter in self.chatters.items():
            chatter.pushMessage(msg)
            chatter.quit()

        return msg

    ###########
    # helpers #
    ###########

    # removes the user from the channel, and delete the channel if no one is in
    # it anymore
    def removeChatterFromChannel(self, chatter, channel):
        chatters_remaining = channel.partWithChatter(chatter)
        if chatters_remaining == 0:
            del self.channels[channel.name]

    def isValidChannelName(self, name):
        return not re.match(r'^#[A-Za-z0-9_.@-]{1,64}$', name) == None

    def isValidUsername(self, name):
        return not re.match(r'^[A-Za-z0-9_.@-]{1,64}$', name) == None
