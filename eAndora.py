"""A Pandora Client Written in Python EFLs/Elm
Uses VLC as a streaming backend
By: Jeff Hoogland (JeffHoogland@Linux.com)
Started: 12/20/12"""

import os
import elementary
import edje
import ecore
import evas
import time
import pandora
import vlc

class eAndora:
    def __init__( self ):
        self.gui = ""
        self.pandora = pandora.Pandora()
        self.curStation = ""
        self.curSong = None
        self.playing = False
        self.skip = False
        self.die = False
        self.settings = {"username":"", "password":""}
        self.player = None
        self.skinName = "Default"
        self.player = vlc.MediaListPlayer()
        self.songlist = vlc.MediaList()
        self.songinfo = []

    def setGUI( self, GUI):
        self.gui = GUI

    def auth( self, user, passwd):
        print "User %s - Password %s"%(user, passwd)
        self.settings['username'] = user
        self.settings['password'] = passwd
        try:
            self.pandora.connect(self.settings['username'], self.settings['password'])
            #self.gui.interface_clicked(None)
        except:
            self.gui.login_error(None)

    def playSong( self ):
        self.playing = True
        self.player.play()

    def pauseSong( self ):
        self.playing = False
        self.player.pause()

    def skipSong( self ):
        self.player.next()

    def setStation( self, station ):
        self.curStation = pandora.Station(self.pandora, station)

    def getStations( self ):
        return self.pandora.get_stations()

    def getStation( self ):
        return self.curStation

    def getSongInfo( self ):
        return self.songinfo

    def getStationFromName( self, name):
        stations = self.getStations()
        for station in stations:
            if station['stationName'] == name:
                return station

    def clearSongs( self ):
        for i in range(len(self.songinfo)-1):
            self.songlist.remove_index(0)
        self.songinfo = []
        self.player.set_media_list(self.songlist)

    def addSongs( self ):
        playlist = self.curStation.get_playlist()
        for song in playlist:
            info = { "title"	:	song.title, \
        	 "artist"	:	song.artist, \
        	 "album"	:	song.album, \
        	 "thumbnail"	:	song.artRadio, \
        	}
            self.songinfo.append(info)
            self.songlist.add_media(str(song.audioUrl))
        self.player.set_media_list(self.songlist)

class Interface:

    def __init__( self ):
        self.ourPlayer = eAndora()
        self.mainWindow = elementary.Window("table", elementary.ELM_WIN_BASIC)
        self.songList = elementary.List(self.mainWindow)
        self.stationButton = elementary.Button(self.mainWindow)

    def close_window(self, bt, win):
        win.delete()

    def login_user(self, bt, user, passwd, win):
        win.hide()
        self.ourPlayer.auth(user.entry_get(), passwd.entry_get())
        self.interface_clicked(None)

    def spawn_login(self, bt, win):
        win.hide()
        self.login_clicked(None)

    def login_error(self, obj):
        win = elementary.Window("test", elementary.ELM_WIN_BASIC)
        win.title_set("eAndora - Error")
        if obj is None:
            win.callback_delete_request_add(lambda o: elementary.exit())

        bg = elementary.Background(win)
        win.resize_object_add(bg)
        bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bg.show()

        box0 = elementary.Box(win)
        box0.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        win.resize_object_add(box0)
        box0.show()

        fr = elementary.Frame(win)
        fr.text_set("There was an issue logging - please try again.")
        box0.pack_end(fr)
        fr.show()

        bt = elementary.Button(win)
        bt.text_set("OK")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.callback_unpressed_add(self.spawn_login, win)
        box0.pack_end(bt)
        bt.show()

        win.show()

    def login_clicked(self, obj):
        self.ourPlayer.setGUI(self)
        win = elementary.Window("table", elementary.ELM_WIN_BASIC)
        win.title_set("eAndora - Login")
        if obj is None:
            win.callback_delete_request_add(lambda o: elementary.exit())

        bg = elementary.Background(win)
        win.resize_object_add(bg)
        bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bg.show()

        tb = elementary.Table(win)
        win.resize_object_add(tb)
        tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        tb.show()

        bt = elementary.Label(win)
        bt.text_set("<div align='center'><b>Email:</b></div>")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.pack(bt, 0, 0, 1, 1)
        bt.show()

        bt = elementary.Label(win)
        bt.text_set("<div align='center'><b>Password:</b></div>")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.pack(bt, 0, 1, 1, 1)
        bt.show()

        log = elementary.Entry(win)
        log.line_wrap_set(False)
        log.entry_set("address")
        log.input_panel_return_key_disabled_set(True)
        log.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        log.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.pack(log, 1, 0, 1, 1)
        log.show()

        pas = elementary.Entry(win)
        pas.line_wrap_set(False)
        pas.entry_set("password")
        pas.input_panel_return_key_disabled = True
        pas.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        pas.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.pack(pas, 1, 1, 1, 1)
        pas.show()

        bt = elementary.Button(win)
        bt.text_set("Login")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.callback_unpressed_add(self.login_user, log, pas, win)
        tb.pack(bt, 0, 2, 1, 1)
        bt.show()

        bt = elementary.Button(win)
        bt.text_set("Exit")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.callback_unpressed_add(self.close_window, win)
        tb.pack(bt, 1, 2, 1, 1)
        bt.show()

        win.resize(640, 320)
        win.show()

    def play_pause(self, bt):
        ic = elementary.Icon(self.mainWindow)
        if self.ourPlayer.playing:
            ic.file_set("images/play.png")
            self.ourPlayer.pauseSong()
        else:
            ic.file_set("images/pause.png")
            self.ourPlayer.playSong()
        bt.content_set(ic)
        bt.show()

    def skip_track(self, bt):
        self.ourPlayer.skipSong()

    def cb_items(self, li, item):
        self.ourPlayer.pauseSong()
        self.ourPlayer.setStation(self.ourPlayer.getStationFromName(item.text))
        self.ourPlayer.clearSongs()
        self.ourPlayer.addSongs()
        self.ourPlayer.skipSong()
        self.ourPlayer.playSong()
        self.refreshInterface(clear=True)
        print(("ctxpopup item selected: %s" % (item.text)))

    def refreshInterface( self, clear=False ):
        if clear:
            self.songList.clear()
        songinfo = self.ourPlayer.getSongInfo()
        for song in songinfo:
            self.songList.item_prepend("%s - %s"%(song['title'], song['artist']))
        self.songList.show()
        self.songList.go()
        self.stationButton.text_set(str(self.ourPlayer.getStation().name))
        self.stationButton.show()

    def item_new(self, cp, label, icon = None):
        if icon:
            ic = elementary.Icon(cp)
            ic.standard_set(icon)
            ic.resizable_set(False, False)
            return cp.item_append(label, ic, self.cb_items)
        else:
            return cp.item_append(label, None, self.cb_items)

    def station_selection(self, bt):
        cp = elementary.Ctxpopup(bt)
        stations = self.ourPlayer.getStations()
        for station in stations:
            bt = self.item_new(cp, str(station['stationName']))
        cp.show()

    def interface_clicked(self, obj):
        #self.ourPlayer.setGUI(self)
        #self.ourPlayer.auth()
        self.ourPlayer.setStation(self.ourPlayer.getStations()[0])
        self.ourPlayer.addSongs()
        self.ourPlayer.playSong()
        self.mainWindow.title_set("eAndora - Internet Radio")
        if obj is None:
            self.mainWindow.callback_delete_request_add(lambda o: elementary.exit())

        bg = elementary.Background(self.mainWindow)
        self.mainWindow.resize_object_add(bg)
        bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bg.show()

        tb = elementary.Table(self.mainWindow)
        self.mainWindow.resize_object_add(tb)
        tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        tb.show()

        self.stationButton.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.stationButton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.stationButton.callback_unpressed_add(self.station_selection)
        tb.pack(self.stationButton, 0, 0, 2, 1)

        self.songList.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.songList.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.pack(self.songList, 0, 1, 2, 3)
        self.refreshInterface()

        ic = elementary.Icon(self.mainWindow)
        ic.file_set("images/pause.png")
        bt = elementary.Button(self.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.play_pause)
        tb.pack(bt, 2, 3, 1, 1)
        bt.show()

        ic = elementary.Icon(self.mainWindow)
        ic.file_set("images/skip.png")
        bt = elementary.Button(self.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.skip_track)
        tb.pack(bt, 2, 2, 1, 1)
        bt.show()

        songinfo = self.ourPlayer.getSongInfo()

        self.mainWindow.resize(800, 480)
        self.mainWindow.show()

if __name__ == "__main__":
    elementary.init()

    GUI = Interface()
    GUI.login_clicked(None)
    
    elementary.run()    
    elementary.shutdown()

