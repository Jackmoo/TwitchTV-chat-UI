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
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()
    
    def close(self):
        self.file.close()

        
class IrcBot(irc.IRCClient):
    
    def connectionMade(self):
        """Called when a connection is made."""
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.logfilename, 'a'))
        self.logger.log("[connected at %s" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        """Called when a connection is lost."""
        irc.IRCClient.connectionLost(self, reason)
        log.msg("connection lost {!r}".format(reason))
        self.logger = MessageLogger(open(self.factory.logfilename, 'a'))
        self.logger.log("[disconnected at %s, since %s" %
                        ( time.asctime(time.localtime(time.time())) , reason )
                       )
        
    # callbacks for events

    def signedOn(self):
        """Called when bot has successfully signed on to server."""
        self.logger.log("signed on")
        self.join(self.factory.channel)

    def joined(self, channel):
        """Called when the bot joins the channel."""
        self.logger.log("[{nick} has joined {channel}]"
                        .format(nick=self.nickname, channel=self.factory.channel))

    def privmsg(self, user, channel, msg):
        """Called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        print("<%s> %s" % (user, msg))
        self.factory.msgQueue.put({'user': user, 'channel': channel, 'msg': msg})

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("**ACTION** %s %s" % (user, msg))
        print("**ACTION** %s %s" % (user, msg))
        
class IrcBotFactory(protocol.ClientFactory):
    # instantiate the TalkBackBot IRC protocol
    # protocol = ircBot
    
    def __init__(self, settings):
        #some init setting
        self.channel = settings['channel']
        self.nickname = settings['nickname']
        self.logfilename = './log/' + settings['channel'] + str(time.time()) + '.log'
        self.password = settings['password']
        #self.quotes = settings.quotes
        #self.triggers = settings.triggers
        self.msgQueue = Queue()
        
    def buildProtocol(self, addr):
        p = IrcBot()
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

