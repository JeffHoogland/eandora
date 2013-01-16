"""A Pandora Client Written in Python EFLs/Elm
Uses Emotion as a streaming backend
By: Jeff Hoogland (JeffHoogland@Linux.com)
Started: 12/20/12


"""

import os
import elementary
import evas
import time
import pandora
import urllib
import webbrowser

#These are all eAndora pieces broken down into multiple files
#GUI Windows
from loginWindow import *
from playerWindow import *
#Pandora Backend Interface
from playerClass import *

class Interface(object):
    def __init__( self ):
        #Main window - where everything other than popups appears
        self.mainWindow = elementary.StandardWindow("eAndora", "eAndora - Internet Radio")
        self.nf = elementary.Naviframe(self.mainWindow)
        self.nf.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.nf.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.nf.show()
        self.mainWindow.resize_object_add(self.nf)
        self.mainWindow.callback_delete_request_add(lambda o: elementary.exit())

        #Our pandora interface instance
        self.ourPlayer = eAndora(self)

    def launch( self ):
        #Resize and display the main window, then login
        self.mainWindow.resize(800, 300)
        self.mainWindow.show()
        self.login()

    def login(self):
        home = os.path.expanduser("~")
        if os.path.exists("%s/.config/eAndora/userinfo"%home):
            f = open('%s/.config/eAndora/userinfo'%home, 'r')
            lines = f.readlines()
            self.ourPlayer.auth(lines[0].rstrip("\n"), lines[1].rstrip("\n"))
            self.spawn_player()
        else:
            self.spawn_login()

    def login_user(self, bt, user, passwd, win, ck):
        #Logs a user in (and writes to a config file if needed) and then pushes the main page
        if ck.state:
            home = os.path.expanduser("~")
            if not os.path.exists("%s/.config/eAndora"%home):
                os.makedirs("%s/.config/eAndora"%home)
            f = open('%s/.config/eAndora/userinfo'%home, 'w')
            f.write('%s\n'%user.entry_get())
            f.write('%s\n'%passwd.entry_get())
            f.close()
        self.ourPlayer.auth(user.entry_get(), passwd.entry_get())
        self.spawn_player()

    def login_error(self):
        popup = elementary.Popup(self.mainWindow)
        #popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "Something went wrong, please try again"
        popup.part_text_set("title,text", "Login Error")
        bt = elementary.Button(self.mainWindow)
        bt.text = "OK"
        bt.callback_clicked_add(self.spawn_login, popup)
        popup.part_content_set("button1", bt)
        popup.show()

    def spawn_login(self, bt=False, win=False):
        #Push the login frame
        self.nf.item_simple_push(loginWindow(self))
        if win:
            win.hide()

    def spawn_player(self, bt=False, win=False):
        #Push the main frame
        self.nf.item_simple_push(playerWindow(self))


if __name__ == "__main__":
    GUI = Interface()
    GUI.launch()
    elementary.run()    
    elementary.shutdown()
