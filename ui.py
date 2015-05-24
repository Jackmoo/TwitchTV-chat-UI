#!/usr/bin/python

# python module
import io, re
import threading
import webbrowser
from collections import deque
try:
    #python2
    import Queue as Queue
except ImportError:
    #py3
    import queue as Queue

# ext module (for image display, resizing)
from PIL import Image, ImageTk
import tkFont

# modules that aren't the same name between py2 and py3
try:
    #python2
    import Tkinter as tk
    from urllib2 import urlopen
except ImportError:
    #py3
    import tkinter as tk
    from uellib.request import urlopen

"""
Author:  Jkm 
Version: 0.1
    
"""    
def show_hand_cursor(event):
    event.widget.configure(cursor="hand2")

def show_arrow_cursor(event):
    event.widget.configure(cursor="")

class TtvChatAppUI(tk.Tk):
    #===================================
    def __init__(self, parent):
        # call super class __init__
        tk.Tk.__init__(self, parent)
        
        #fixed variables
        
        #define font
        self.msgFont = tkFont.Font(family="Helvetica")
        self.usernameFont = tkFont.Font(family="Helvetica", size="10")
        # font format params (by sequence):
        # family ex."Helvetica"
        # size ex."10"
        # weight "bold" or "normal"
        # slant "italic" or "roman"
        # underline "1" or "0"
        # overstrike "1" or "0"
        
        # this is the maximum number of saved image reference to stop GC collect it
        # if any image is dereference, the image would be blank
        # however, too large number may consume lots of memory
        self.imageDeque = deque(maxlen=5)

        # the maximum height and width of (resized)image displayed in chat window
        self.IMAGE_MAX_HEIGHT = 300
        self.IMAGE_MAX_WIDTH = 300
        
        self.MAX_LINE_NUMBER = 1024
        
        # queue of msg from UI -> ircBot
        self.uiSentMsgQueue = Queue.Queue()
        self.uiRecvMsgQueue = Queue.Queue()
        
        # init function of creating UI cpmponent
        self.initUI()
        
        
    #===================================
    
    # Method
    def loadUrlImage(self, url, maxHeight, maxWidth):
        #load from internet
        image_bytes = urlopen(url).read()
        data_stream = io.BytesIO(image_bytes)

        pil_image = Image.open(data_stream)
        w, h = pil_image.size
        
        #check resize ratio
        resizeRatio = 1.0
        resizeRatio = min( 1, min(float(maxWidth)/w, float(maxHeight)/h) )
        resizedImage = pil_image.resize( (int(w*resizeRatio), int(h*resizeRatio) )
                                        ,Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resizedImage)
        #photo = tk.PhotoImage(file='./ttHbza.gif')
        
        return photo

    def btnSendMsg(self):
        inputMsg = self.typeMsg.get('0.0', tk.END)
        while inputMsg[-1] == '\n' or inputMsg[-1] == '\r':
            inputMsg = inputMsg[:-1]
        inputMsg = inputMsg.encode('utf-8')
        sendMsg = {'user':'me', 'msg':inputMsg, 'color':'black'}
        self.handleMsg(sendMsg)
        self.uiSentMsgQueue.put({'msg': inputMsg })
        self.typeMsg.delete('0.0', tk.END)
        
    def clearChatMsg(self):
        self.chatMsg.delete('0.0', tk.END)
        
    def handleMsg(self, recvMsg):
        # recvMsg = {'user': user, 'channel': channel, 'msg': msg, 'color': color}
        msgHeader = recvMsg['user'] + ':\n'
        # chatMsg tags (username color)
        self.chatMsg.tag_config(recvMsg['user'], 
                                 font=("Helvetica", "12", "bold"), 
                                 foreground=recvMsg['color']
                               )
        self.chatMsg.insert(tk.END, msgHeader, (recvMsg['user']))
        # check url
        isImageUrl = re.match('^https?://(?:[a-z\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png)$', recvMsg['msg'])
        if isImageUrl:
            self.chatMsg.tag_config(recvMsg['msg'], foreground='blue', underline=1)
            # cursor enter hyperlink shows 'hand'
            self.chatMsg.tag_bind(recvMsg['msg'], "<Enter>", show_hand_cursor)
            # cursor leave hyperlink shows 'normal cursor'
            self.chatMsg.tag_bind(recvMsg['msg'], "<Leave>", show_arrow_cursor)
            # browser hyperlink 
            self.chatMsg.tag_bind(recvMsg['msg'], '<Button-1>', lambda e, arg=recvMsg['msg']: webbrowser.open(arg))
            self.chatMsg.insert(tk.END, recvMsg['msg']+'\n', (recvMsg['msg']))
            self.appendImage(recvMsg['msg'])
        else:
            self.chatMsg.insert(tk.END, recvMsg['msg'])
        self.chatMsg.insert(tk.END, '\n \n')
        currentLineNumber = int(self.chatMsg.index('end-1c').split('.')[0])
        if currentLineNumber > self.MAX_LINE_NUMBER:
            self.chatMsg.delete('0.0', str(currentLineNumber-self.MAX_LINE_NUMBER)+'.0')
        self.chatMsg.see(tk.END)

    def appendImage(self, url):
        loadedImage = self.loadUrlImage(url, self.IMAGE_MAX_HEIGHT, self.IMAGE_MAX_WIDTH)
        self.chatMsg.image_create(tk.END, image=loadedImage)
        # keep the image reference in deque
        self.imageDeque.append(loadedImage)

    # def looping handler function of chatMsg
    def chatMsgRecvUpdateHandler(self):
        try:
            while 1:
                recvMsg = self.uiRecvMsgQueue.get_nowait()
                if recvMsg is not None:
                    self.handleMsg(recvMsg)
                self.chatMsg.update_idletasks()
        except Queue.Empty:
            pass
        self.chatMsg.after(100, self.chatMsgRecvUpdateHandler)
        
    def initUI(self):
        #====================================
        # UI
        # basic layout
        self.chatFrame = tk.Frame(self, width=400, height=600, bg='white')
        self.typeFrame = tk.Frame(self, width=400, height=100, bg='white')
        self.btnFrame = tk.Frame(self, width=400, height=30)
        self.btnFrame2 = tk.Frame(self, width=400, height=30)
        #fix basic frames size
        self.chatFrame.pack_propagate(0)
        self.typeFrame.pack_propagate(0)
        self.btnFrame.pack_propagate(0)
        self.btnFrame2.pack_propagate(0)
        #pack basic Frame
        self.chatFrame.pack()
        self.typeFrame.pack()
        self.btnFrame.pack()
        self.btnFrame2.pack()
        
        # 2nd layer layout
        # chatMsg Text
        self.chatMsg = tk.Text(self.chatFrame, font=self.msgFont)
        
        # scrollbar of chatMsg
        self.chatScrollbar = tk.Scrollbar(self.chatFrame)
        self.chatMsg.configure(yscrollcommand=self.chatScrollbar.set)
        self.chatScrollbar.config(command=self.chatMsg.yview)
        
        #DONT MODIFY SEQENCE, pack scrollbar 1st, then Text to get best result 
        self.chatScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chatMsg.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # typeMsg Text
        self.typeMsg = tk.Text(self.typeFrame)
        self.typeMsg.pack(fill=tk.BOTH)
        
        # btns
        self.sendBtn = tk.Button(self.btnFrame, text='send', command=self.btnSendMsg)
        self.sendBtn2 = tk.Button(self.btnFrame2, text='clear', command=self.clearChatMsg)
        self.sendBtn.pack()    
        self.sendBtn2.pack()
        
        # trigger chatMsg handler
        self.chatMsg.after(100, self.chatMsgRecvUpdateHandler)
        

if __name__ == '__main__':
    app = TtvChatAppUI(None)
    app.title('test app')
    app.mainloop() #8
