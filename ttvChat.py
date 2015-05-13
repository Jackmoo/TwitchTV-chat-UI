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
        self.start()
        
    def run(self):
        print 'UI thread online\n'
        # block here
        self.appUI.mainloop()
        # end the main thread
        os._exit(1)
uiThread = uiThread()


# load parsing bot
print 'preparing irc bot...'
f = IrcBotFactory(settings)
reactor.connectTCP(settings['ircServer'], settings['ircPort'], f)

# send bot msg queue to UI
print 'preparing event thread...'
class eventThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        
    def run(self):
        print 'event thread online\n'
        if uiThread.appUI:
            while 1:
                qitem = f.msgQueue.get()
                uiThread.appUI.handleMsg(qitem['user'],qitem['msg'])           
eventThread = eventThread()

# bot main loop
print 'parsing bot online'
reactor.run()


