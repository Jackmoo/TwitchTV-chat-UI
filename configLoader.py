#!/usr/bin/python

from ConfigParser import ConfigParser
    
class ConfigLoader:
    def load(self, filename):
        configParser = ConfigParser()
        settings = {}
        if filename:
            configParser.read(filename)

            settings['endPoint'] = configParser.get('irc_ttv', 'endPoint')
            settings['nickname'] = configParser.get('irc_ttv', 'nickname')
            settings['password'] = configParser.get('irc_ttv', 'password')
            settings['channel'] = configParser.get('irc_ttv', 'channel')
            settings['ircServer'] = configParser.get('irc_ttv', 'ircServer')
            settings['ircPort'] = configParser.getint('irc_ttv', 'ircPort')
        
        return settings
        
if __name__ == '__main__':
    p = ConfigLoader()
    settings = p.load('settings.ini')
    print settings