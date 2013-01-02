"""A Pandora Client Written in Python EFLs/Elm
Uses VLC as a streaming backend
By: Jeff Hoogland (JeffHoogland@Linux.com)
Started: 12/20/12


"""

import os
import elementary
import edje
import ecore
import evas
import time
import pandora
import vlc
import urllib

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
        self.song = None
        self.songinfo = []
        self.player = vlc.MediaPlayer()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,      self.nextSong)
        self.counter = 0

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
        self.nextSong("skip")

    def setStation( self, station ):
        self.curStation = pandora.Station(self.pandora, station)

    def getStations( self ):
        return self.pandora.get_stations()

    def getStation( self ):
        return self.curStation

    def getCurSongInfo( self ):
        return self.songinfo[self.curSong]

    def getSongInfo( self ):
        return self.songinfo

    def getStationFromName( self, name):
        stations = self.getStations()
        for station in stations:
            if station['stationName'] == name:
                return station

    def getSongDuration( self ):
        seconds = self.player.get_length() / 1000.0
        mins = 0
        while seconds >= 60:
            seconds -= 60
            mins += 1
        return mins, seconds

    def clearSongs( self ):
        self.song = None
        self.songinfo = []

    def addSongs( self ):
        playlist = self.curStation.get_playlist()
        for song in playlist:
            info = { "title"	:	song.title, \
        	 "artist"	:	song.artist, \
        	 "album"	:	song.album, \
        	 "thumbnail"	:	song.artRadio, \
             "url"      : str(song.audioUrl)
        	}
            self.songinfo.append(info)
        if not self.song:
            self.startPlaying()
        self.gui.refreshInterface()

    def startPlaying( self ):
        self.curSong = -1
        self.nextSong()

    def nextSong( self , event=False):
        #print("Debug 1")
        if self.player.is_playing():
            self.player.stop()
        else:
            #print("Debug 11")
            self.player = vlc.MediaPlayer()
            self.event_manager = self.player.event_manager()
            self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,      self.nextSong)
        #print("Debug 2")
        self.curSong += 1
        #print("Debug 2")
        if self.curSong >= len(self.songinfo)-1:
            #print("Debug 3")
            self.addSongs()
        #print("Debug 4")
        info = self.songinfo[self.curSong]
        self.song = info['title']
        #print(info)
        #print("Debug 5")
        self.player.set_media(vlc.Media(info['url']))
        #print("Debug 6")
        self.playing = True
        self.player.play()
        #print("Debug 7")
        self.gui.song_change()

class Interface:

    def __init__( self ):
        self.ourPlayer = eAndora()
        self.mainWindow = elementary.Window("table", elementary.ELM_WIN_BASIC)
        self.songList = elementary.List(self.mainWindow)
        self.stationButton = elementary.Button(self.mainWindow)
        #self.stationDropdown = elementary.Toolbar(self.mainWindow)
        self.tb = None
        self.thumb = elementary.Button(self.mainWindow)
        self.song = elementary.Button(self.mainWindow)
        self.artist = elementary.Button(self.mainWindow)
        self.album = elementary.Button(self.mainWindow)
        self.counter = [elementary.Clock(self.mainWindow), elementary.Label(self.mainWindow), elementary.Label(self.mainWindow)]
        self.pauseTime = None

    def song_change( self ):
        info = self.ourPlayer.getCurSongInfo()
        try:
            os.remove('/tmp/albumart.jpg')
        except:
            pass
        urllib.urlretrieve(str(info['thumbnail']), '/tmp/albumart.jpg')
        ic = elementary.Icon(self.mainWindow)
        ic.file_set('/tmp/albumart.jpg')
        self.thumb.show()
        self.thumb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.thumb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.thumb.content_set(ic)
        self.tb.pack(self.thumb, 2, 0, 2, 3)
        self.thumb.show()

        self.song.hide()
        self.song.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.song.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.song.text_set("Song: %s"%info['title'])
        self.tb.pack(self.song, 0, 0, 2, 1)
        self.song.show()

        self.artist.hide()
        self.artist.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.artist.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.artist.text_set("Artist: %s"%info['artist'])
        self.tb.pack(self.artist, 0, 1, 2, 1)
        self.artist.show()

        self.album.hide()
        self.album.text_set("Album: %s"%info['album'])
        self.album.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.album.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.album, 0, 2, 2, 1)
        self.album.show()

        self.counter[0].hide()
        self.counter[0].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.counter[0].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.counter[0].show_seconds_set(True)
        self.counter[0].time_set(0, 0, 0)
        self.tb.pack(self.counter[0], 0, 3, 1, 1)
        self.counter[0].show()

        self.counter[1].hide()
        self.counter[1].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.counter[1].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        time.sleep(0.5)
        mins, seconds = self.ourPlayer.getSongDuration()
        if int(seconds) > 9:
            self.counter[1].text_set("<b>/      %s : %s</b>"%(mins, int(seconds)))
        else:
            self.counter[1].text_set("<b>/      %s : 0%s</b>"%(mins, int(seconds)))
        self.tb.pack(self.counter[1], 2, 3, 1, 1)
        self.counter[1].show()

        print("Hey look the song changed!")

    def close_window(self, bt, win):
        win.delete()

    def login_user(self, bt, user, passwd, win, ck):
        win.hide()
        if ck.state:
            home = os.path.expanduser("~")
            if not os.path.exists("%s/.config/eAndora"%home):
                os.makedirs("%s/.config/eAndora"%home)
            f = open('%s/.config/eAndora/userinfo'%home, 'w')
            f.write('%s\n'%user.entry_get())
            f.write('%s\n'%passwd.entry_get())
            f.close()
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

    def login(self, obj):
        self.ourPlayer.setGUI(self)
        home = os.path.expanduser("~")
        if os.path.exists("%s/.config/eAndora/userinfo"%home):
            f = open('%s/.config/eAndora/userinfo'%home, 'r')
            lines = f.readlines()
            self.ourPlayer.auth(lines[0].rstrip("\n"), lines[1].rstrip("\n"))
            self.interface_clicked(None)
        else:
            self.login_clicked(None)

    def login_clicked(self, obj):
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

        ck = elementary.Check(win)
        ck.text_set("Store Login")
        #ck.callback_changed_add(ck_3)
        tb.pack(ck, 0, 2, 1, 1)
        ck.show()

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
        pas.password = True
        pas.input_panel_return_key_disabled = True
        pas.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        pas.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.pack(pas, 1, 1, 1, 1)
        pas.show()

        bt = elementary.Button(win)
        bt.text_set("Login")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.callback_unpressed_add(self.login_user, log, pas, win, ck)
        tb.pack(bt, 0, 3, 2, 1)
        bt.show()

        bt = elementary.Button(win)
        bt.text_set("Exit")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.callback_unpressed_add(self.close_window, win)
        tb.pack(bt, 0, 4, 2, 1)
        bt.show()

        win.resize(800, 300)
        win.show()

    def play_pause(self, bt):
        ic = elementary.Icon(self.mainWindow)
        if self.ourPlayer.playing:
            ic.file_set("images/play.png")
            self.pauseTime = self.counter[0].time_get()
            self.counter[0].hide()
            self.counter[2].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            self.counter[2].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            if self.pauseTime[2] > 9:
                self.counter[2].text_set("<b>%s : %s</b>"%(self.pauseTime[1], self.pauseTime[2]))
            else:
                self.counter[2].text_set("<b>%s : 0%s</b>"%(self.pauseTime[1], self.pauseTime[2]))
            self.tb.pack(self.counter[2], 0, 3, 1, 1)
            self.counter[2].show()
            self.ourPlayer.pauseSong()
        else:
            ic.file_set("images/pause.png")
            self.counter[2].hide()
            self.counter[0].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            self.counter[0].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            self.counter[0].show_seconds_set(True)
            self.counter[0].time_set(0, self.pauseTime[1], self.pauseTime[2])
            self.tb.pack(self.counter[0], 0, 3, 1, 1)
            self.counter[0].show()
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
        self.ourPlayer.playSong()
        self.refreshInterface(clear=True)
        print(("ctxpopup item selected: %s" % (item.text)))

    def refreshInterface( self, clear=False ):
        if clear:
            self.songList.clear()
        songinfo = self.ourPlayer.getSongInfo()
        for song in songinfo:
            if songinfo.index(song) >= len(songinfo) - 4:
                self.songList.item_prepend("%s - %s"%(song['title'], song['artist']))
        self.songList.show()
        self.songList.go()
        self.stationButton.text_set(str(self.ourPlayer.getStation().name))
        self.stationButton.hide()
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
        #self.ourPlayer.auth("jeffhoogland@linux.com", "")
        self.ourPlayer.setStation(self.ourPlayer.getStations()[0])
        self.mainWindow.title_set("eAndora - Internet Radio")
        ic = elementary.Icon(self.mainWindow)
        ic.file_set("images/eAndora.png")
        self.mainWindow.icon_object_set(ic)
        if obj is None:
            self.mainWindow.callback_delete_request_add(lambda o: elementary.exit())

        bg = elementary.Background(self.mainWindow)
        self.mainWindow.resize_object_add(bg)
        bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bg.show()

        self.tb = elementary.Table(self.mainWindow)
        self.mainWindow.resize_object_add(self.tb)
        self.tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.tb.show()

        self.stationButton.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.stationButton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.stationButton.callback_unpressed_add(self.station_selection)
        self.tb.pack(self.stationButton, 4, 0, 2, 3)

        self.songList.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.songList.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.songList, 0, 4, 4, 3)

        ic = elementary.Icon(self.mainWindow)
        ic.file_set("images/pause.png")
        bt = elementary.Button(self.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.play_pause)
        self.tb.pack(bt, 4, 5, 1, 1)
        bt.show()

        ic = elementary.Icon(self.mainWindow)
        ic.file_set("images/skip.png")
        bt = elementary.Button(self.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.skip_track)
        self.tb.pack(bt, 4, 4, 1, 1)
        bt.show()

        songinfo = self.ourPlayer.getSongInfo()

        self.mainWindow.resize(800, 300)
        self.mainWindow.show()
        self.ourPlayer.addSongs()

if __name__ == "__main__":
    elementary.init()

    GUI = Interface()
    GUI.login(None)
    #GUI.interface_clicked(None)
    elementary.run()    
    elementary.shutdown()

