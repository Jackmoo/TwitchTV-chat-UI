#!/usr/bin/python

# === internal module ===
import threading
import os
# === external module ===
from twisted.internet import reactor
# === project module === 
from configLoader import ConfigLoader
from ui import TtvChatAppUI
from bot import IrcBotFactory


# load ini
print 'loading setting....'
p = ConfigLoader()
settings = p.load('settings.ini')

# init UI thread
print 'preparing UI thread....'
class uiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.appUI = TtvChatAppUI(None)
        self.appUI.title('moo Chat')
        self.start()
        
    def run(self):
        print '\n===UI thread online===\n'
        # block here
        self.appUI.mainloop()
        # end the main thread when UI is closed
        os._exit(1)
uiThread = uiThread()


# load parsing bot
print 'preparing irc bot...'
f = IrcBotFactory(settings)
reactor.connectTCP(settings['ircServer'], settings['ircPort'], f)

# send bot msg queue to UI
print 'preparing recv thread...'
class recvMsgThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        
    def run(self):
        print '\n===recv thread online===\n'
        if uiThread.appUI:
            while 1:
                # pass received msg from bot to UI
                botRecvMsg = f.botRecvMsgQueue.get()
                uiThread.appUI.handleMsg(botRecvMsg)
                
recvMsgThread = recvMsgThread()

# send UI msg queue to bot
print 'preparing send thread...'
class sendMsgThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        
    def run(self):
        print '\n===send thread online===\n'
        if uiThread.appUI:
            while 1:
                # pass ui sent msg to bot
                uiSentMsg = uiThread.appUI.uiSentMsgQueue.get()
                if uiSentMsg:
                    f.protocol.say(settings['channel'] , uiSentMsg['msg'])
                    #send pure msg to IRC server
                    #f.protocol.sendLine(uiSentMsg['msg'])
                
sendMsgThread = sendMsgThread()


# bot main loop
print 'parsing bot online'
reactor.run()


