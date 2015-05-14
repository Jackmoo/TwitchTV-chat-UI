----------------
I. Description
----------------
This is a Python based Twitch TV chat program, focusing on:
* display hyperlinked images in chat
* (TODO)other bot-liked reaction (auto-ban, auto-kick, ...)
* log all chat msg


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
*py2exe (OPTIONAL, ONLY FOR WINDOWS)
	- build stand alone .exe file (remember to check if you are authorized to distribute the related libraries).

Built in modules:
* Tkinter
	- all UI
* ConfigParser
	- parsing .ini files
	
-----------------------
III. How to start
-----------------------

* First, you must ensure all the dependency was installed or callable (check pip).
* Second, rename 'settings_default.ini' to 'settings.ini', the 'settings.ini' is the file that saved all settings.
* (OPTIONAL) If you using py2exe to build a runnable .exe file, you could run 'py2exe.bat' to directly build it.


-----------------------
IV. File description
-----------------------

* ttvChat.py
	- main program entry point init module and threads
* ui.py 
	- program UI module
* configLoader.py 
	- settings.ini loader
* bot.py
	- parsing bot, handling data from IRC
* settings_default.ini
	- saved login/channel data, should be renamed to settings.ini to work properly 
* p2exeSetup.py (OPTIONAL)
	- py2exe build script
* py2exe.bat (OPTIONAL)
	- windowns bat, calling p2exeSetup.py to build
	

-----------------------
V. Program structure
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
VI. TODO
-----------------------
 
* sending msg function
* other bot-liked reaction (auto-ban, auto-kick, ...)
* configure setting in UI?
*
