#!/usr/bin/python

from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.words.protocols import irc

import time, sys

try:
    #python2
    from Queue import Queue
except ImportError:
    #py3
    from queue import Queue


''' example i/o
< PASS oauth:twitch_oauth_token
< NICK twitch_username
> :tmi.twitch.tv 001 twitch_username :connected to TMI
> :tmi.twitch.tv 002 twitch_username :your host is TMI
> :tmi.twitch.tv 003 twitch_username :this server is pretty new
> :tmi.twitch.tv 004 twitch_username tmi.twitch.tv 0.0.1 w n
> :tmi.twitch.tv 375 twitch_username :- tmi.twitch.tv Message of the day - 
> :tmi.twitch.tv 372 twitch_username :- not much to say here
> :tmi.twitch.tv 376 twitch_username :End of /MOTD command
'''
class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file
    
    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime())
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()
    
    def close(self):
        self.file.close()

        
class IrcBot(irc.IRCClient):
    
    def connectionMade(self):
        """Called when a connection is made."""
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        self.msgUserColor = {}
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.logfilename, 'a'))
        self.logger.log("[connected at %s" %
                        time.asctime(time.localtime()))

    def connectionLost(self, reason):
        """Called when a connection is lost."""
        irc.IRCClient.connectionLost(self, reason)
        log.msg("connection lost {!r}".format(reason))
        self.logger = MessageLogger(open(self.factory.logfilename, 'a'))
        self.logger.log("[disconnected at %s, since %s" %
                        ( time.asctime(time.localtime()) , reason )
                       )
        
    # callbacks for events

    def signedOn(self):
        """Called when bot has successfully signed on to server."""
        self.logger.log("signed on")
        self.join(self.factory.channel)
        # when joined channel, sent 'TWITCHCLIENT 2' + '\r\n' to get detail user data
        self.sendLine('TWITCHCLIENT 2')
        self.logger.log('send ttvclient 2')

    def joined(self, channel):
        """Called when the bot joins the channel."""
        # LOOKS LIKE THIS IS NEVER CALLED
        self.logger.log("[{nick} has joined {channel}]"
                        .format(nick=self.nickname, channel=self.factory.channel))
        

    def privmsg(self, user, channel, msg):
        """Called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        print("<%s> %s" % (user, msg))
        
        # handle jtv sent msg (USERCOLOR, EMOTESET)
        # example
        # USERCOLOR boy20330 #FF0000
        # EMOTESET boy20330 [0,3568]
        # CLEARCHAT (all chat is clear)
        # CLEARCHAT boy20330 (user boy20330 is timeout/ban, <message delete> at chat)
        if user == 'jtv':
            # splitMsg = msgConfig, *user, *config
            splitMsg = msg.split(' ',2)
            if splitMsg[0] == 'USERCOLOR':
                self.msgUserColor[splitMsg[1]] = splitMsg[2]
            # elif splitMsg[0] == 'EMOTESET':
                #TODO
            # elif splitMsg[0] == 'CLEARCHAT':
                #TODO
        else:
            # default color, sometimes the jtv doesn't send color data
            color = 'black'
            # each color only used once, then delete it in dict
            """
            sometimes the color data does not send with seq
            for instance:
                USERCOLOR boy      #FF0000 ---> add boy's color to dict
                USERCOLOR nika #FF0000     ---> add nika's color to dict
                (nika's msg)               <--- get nika's color from dict, then del
                (boy's msg)                <--- get boy's color from dict, then del
            so it's necessary to preserve the color data
            once the data was used, it will be deleted
            """
            if user in self.msgUserColor:
                color = self.msgUserColor[user]
                del self.msgUserColor[user]
            self.factory.botRecvMsgQueue.put({'user': user, 'channel': channel, 'msg': msg, 'color': color})

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("**ACTION** %s %s" % (user, msg))
        print("**ACTION** %s %s" % (user, msg))
        
    # server->client messages
    def irc_PING(self, prefix, params):
        self.logger.log("PING ACCEPT %s %s" % (prefix, params))
        self.sendLine("PONG %s" % params[-1])
        self.logger.log("PING RESPONSE: PONG %s" % params[-1])
      
class IrcBotFactory(protocol.ClientFactory):
    # instantiate the TalkBackBot IRC protocol
    # protocol = ircBot
    
    def __init__(self, settings):
        #some init setting
        self.channel = settings['channel']
        self.nickname = settings['nickname']
        self.logfilename = './log/' \
                           + settings['channel'] \
                           + time.strftime("%Y%m%d_%H_%M_%S", time.localtime()) \
                           + '.log'
        self.password = settings['password']
        #self.quotes = settings.quotes
        #self.triggers = settings.triggers
        self.botRecvMsgQueue = Queue()
        
    def buildProtocol(self, addr):
        self.protocol = IrcBot()
        p = self.protocol
        p.factory = self
        return p
        
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed: %s" % reason)
        reactor.stop()
    
if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

