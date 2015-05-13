----------------
I. Description
----------------
This is a Python based Twitch TV chat program, focusing on:
	- display hyperlinked images in chat
	- (TODO)other bot-liked reaction (auto-ban, auto-kick, ...)
	- log all chat msg


----------------
II. Dependency
----------------
This program was written in Python 2.7, Python 3 capability isn't test yet.

Required following external Python Modules:
* Twisted 
	- IRC protocol parsing 
* Zope
	- required by Twisted
* PIL
	- image ( .jpg, .png, ...etc) cability 
	- image processing (resizing)
	
Built in modules:
* Tkinter
	- all UI
* ConfigParser
	- parsing .ini files
	

-----------------------
III. Program structure
-----------------------
     
                                                             +----------------+        +-------------+
                                                             |   ttvChat.py   |        | settins.ini |
                                                             +-------+--------+        +------+------+
                                                                     |                        |       
                                                                     |         load in        |       
                                                                     | <----------------------+       
               +-----------------------------------------------------+                                
               |                                                     |                                
               |                                                     |                                
               |                          +--------------------------+                                
               |                          |                          |                                
               |                          |                          |                                
               |                          |                          |                                
               |                          |                          |                                
               |                          |                          |                                
               |                          |                          |                                
     +---------+----------+      +--------+-----------+      +-------+---------+                      
     |  ui.py             |      | event thread       |      |   main thread   |                      
     |  UI thread, loop   | <--> | handle msg between | <--> |(bot.py instance)|                      
     |  by mainloop()     |      | ui and bot         |      | twisted reactor |                      
     +--------------------+      +--------------------+      | parsing channel |                      
                                                             +-----------------+                      

 
drew by asciiflow.com (AWESOME!)

-----------------------
IV. TODO
-----------------------
 
* sending msg function
* other bot-liked reaction (auto-ban, auto-kick, ...)
* configure setting in UI?
*