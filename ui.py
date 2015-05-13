#!/usr/bin/python

# python module
import io, re
from collections import deque

# ext module (for image display, resizing)
from PIL import Image, ImageTk

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
class TtvChatAppUI(tk.Tk):
    #===================================
    def __init__(self, parent):
        # call super class __init__
        tk.Tk.__init__(self, parent)
        
        #fixed variables
        # temp url for image
        # url='http://jkm.twbbs.org/futaba/src/1431003997516.jpg'
        
        # this is the maximum number of saved image reference to stop GC collect it
        # if any image is dereference, the image would be blank
        # however, too large number may consume lots of memory
        self.imageDeque = deque(maxlen=5)

        # the maximum height and width of (resized)image displayed in chat window
        self.IMAGE_MAX_HEIGHT = 300
        self.IMAGE_MAX_WIDTH = 300
        
        self.parent = parent

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
        self.handleMsg('theSendBtn', inputMsg)
        self.typeMsg.delete('0.0', tk.END)
        
    def clearChatMsg(self):
        self.chatMsg.delete('0.0', tk.END)
        
    def handleMsg(self, username, inputMsg):
        msgHeader = username + ':\n'
        self.chatMsg.insert(tk.END, msgHeader)
        isImageUrl = re.match('^https?://(?:[a-z\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png)$', inputMsg)
        if isImageUrl:
            self.appendImage(inputMsg)
        else:
            self.chatMsg.insert(tk.END, inputMsg)
        self.chatMsg.insert(tk.END, ' \n')
        self.chatMsg.see(tk.END)

    def appendImage(self, url):
        loadedImage = self.loadUrlImage(url, self.IMAGE_MAX_HEIGHT, self.IMAGE_MAX_WIDTH)
        self.chatMsg.image_create(tk.END, image=loadedImage)
        self.imageDeque.append(loadedImage)
        
    def initUI(self):
        #====================================
        # UI
        # basic layout
        self.chatFrame = tk.Frame(self, width=380, height=600, bg='white')
        self.typeFrame = tk.Frame(self, width=380, height=100, bg='white')
        self.btnFrame = tk.Frame(self, width=380, height=30)
        self.btnFrame2 = tk.Frame(self, width=380, height=30)
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
        self.chatMsg = tk.Text(self.chatFrame)
        
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
        
    
if __name__ == '__main__':
    app = TtvChatAppUI(None)
    app.title('test app')
    app.mainloop() #8
