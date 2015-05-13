#!/usr/bin/python

from ConfigParser import ConfigParser

from twisted.application.service import IServiceMaker, Service
from twisted.internet.endpoints import clientFromString
from twisted.plugin import IPlugin
from twisted.python import log
from zope.interface import implementer

from bot import IrcBotFactory
from configLoader import ConfigLoader
#

class IrcBotService(Service):
    _bot = None

    def __init__(self, settings):
        self._settings = settings
        
    def startService(self):
        """Construct a client & connect to server."""
        from twisted.internet import reactor
        
        def connected(bot):
            self._bot = bot
        
        def failure(err):
            log.err(err, _why='Could not connect to specified server.')
            reactor.stop()
            
        client = clientFromString(reactor, self._settings.endPoint)
        factory = IrcBotFactory(
            self._settings
        )

    def stopService(self):
        """Disconnect."""
        if self._bot and self._bot.transport.connected:
            self._bot.transport.loseConnection()

@implementer(IServiceMaker, IPlugin)
class IrcBotServiceMaker(object):
    tapname = "ircBot"
    settingFileName = 'settings.ini'
    parser = ConfigLoader()
    
    def makeService(self, options):
        settings = parser.load(settingFileName)
        return IrcBotService(settings)
    
serviceMaker = IrcBotServiceMaker()
        
        