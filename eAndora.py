"""A Pandora Client Written in Python EFLs/Elm
Uses Emotion as a streaming backend
By: Jeff Hoogland (JeffHoogland@Linux.com)
Started: 12/20/12


"""

import os
import elementary
import edje
import ecore
import evas
import emotion
import time
import pandora
import urllib
import webbrowser

def openBrowser(url):
    print "Opening %s"%url
    webbrowser.open(url)
    try:
        os.wait() # workaround for http://bugs.python.org/issue5993
    except:
        pass

class eAndora:
    def __init__( self ):
        self.gui = ""
        self.pandora = pandora.Pandora()
        self.curStation = ""
        self.curSong = None
        self.skip = False
        self.die = False
        self.settings = {"username":"", "password":""}
        self.player = None
        self.skinName = "Default"
        self.song = None
        self.songinfo = []
        self.displaysongs = []
        self.songCount = 0

    def setGUI( self, GUI):
        self.gui = GUI
        self.player = emotion.Emotion(self.gui.mainWindow.evas_get(), module_filename="gstreamer")
        self.player.callback_add("playback_finished", self.nextSong)

    def auth( self, user, passwd):
        print "User %s - Password %s"%(user, passwd)
        self.settings['username'] = user
        self.settings['password'] = passwd
        try:
            self.pandora.connect(self.settings['username'], self.settings['password'])
        except:
            self.gui.login_error(None)

    def playSong( self ):
        self.player.play_set(True)

    def pauseSong( self ):
        self.player.play_set(False)

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
        print "Getting Song duration"
        seconds = self.player.play_length
        print "Starting Seconds %s"%seconds
        mins = 0
        while seconds >= 60:
            seconds -= 60
            mins += 1
        print "Minutes %s Seconds %s"%(mins, seconds) 
        return mins, seconds

    def getSongRating( self ):
        return self.songinfo[self.curSong]['rating']

    def showSong( self ):
        openBrowser(self.songinfo[self.curSong]['object'].songDetailURL)

    def showAlbum( self ):
        openBrowser(self.songinfo[self.curSong]['object'].albumDetailURL)

    def banSong( self ):
        info = self.songinfo[self.curSong]
        info['object'].rate('ban')

    def loveSong( self ):
        info = self.songinfo[self.curSong]
        info['object'].rate('love')

    def clearSongs( self ):
        self.song = None
        self.songCount = 0
        self.songinfo = []
        self.displaysongs = []

    def addSongs( self ):
        playlist = self.curStation.get_playlist()
        for song in playlist:
            info = { "title"	:	song.title, \
        	 "artist"	:	song.artist, \
        	 "album"	:	song.album, \
        	 "thumbnail"	:	song.artRadio, \
             "url"      : str(song.audioUrl), \
             "rating"   : song.rating, \
             "object"   : song
        	}
            self.songinfo.append(info)
        if not self.song:
            self.startPlaying()

    def startPlaying( self ):
        self.curSong = -1
        self.nextSong()

    def nextSong( self , event=False ):
        print("Debug 1")
        if self.player:
            if self.player.play_get():
                self.player.play_set(False)
        #print("Debug 2")
        #self.player = emotion.Emotion(self.gui.mainWindow.evas_get(), module_filename="xine")
        #self.player.callback_add("playback_finished", self.nextSong)
        print("Debug 3")
        self.curSong += 1
        info = self.songinfo[self.curSong]
        self.displaysongs.append(info)
        self.song = info['title']
        print(info)
        print("Debug 4")
        self.player.file = info['url']
        print("Debug 5")
        self.player.play_set(True)
        print("Debug 6")
        self.gui.song_change()
        print("Debug 7")
        #self.curSong += 1
        if self.curSong >= len(self.songinfo)-1:
            print("Debug 8")
            self.addSongs()
        print("Debug 9")
        self.songCount += 1
        if self.songCount >= 15:
            print("Debug 10")
            self.songCount = 0
            self.auth(self.settings['username'], self.settings['password'])

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
        #self.song.style_set("anchor")
        self.artist = elementary.Label(self.mainWindow)
        self.album = elementary.Button(self.mainWindow)
        #self.album.style_set("anchor")
        self.rating = elementary.Button(self.mainWindow)
        self.counter = [elementary.Clock(self.mainWindow), elementary.Label(self.mainWindow), elementary.Label(self.mainWindow)]
        self.pauseTime = None

    def ban_track( self, bt ):
        self.ourPlayer.banSong()
        self.ourPlayer.skipSong()

    def love_track( self, bt ):
        self.ourPlayer.loveSong()
        ic = elementary.Icon(self.mainWindow)
        ic.file_set('images/love.png')
        self.rating.hide()
        self.rating.tooltip_text_set("Song already liked")
        self.rating.content_set(ic)
        self.rating.show()

    def show_song( self, bt ):
        self.ourPlayer.showSong()

    def show_album( self, bt ):
        self.ourPlayer.showAlbum()

    def song_change( self ):
        info = self.ourPlayer.getCurSongInfo()
        print("DEBUG: Changing Album Art")
        try:
            os.remove('/tmp/albumart.jpg')
        except:
            pass
        urllib.urlretrieve(str(info['thumbnail']), '/tmp/albumart.jpg')
        ic = elementary.Icon(self.mainWindow)
        ic.file_set('/tmp/albumart.jpg')
        self.thumb.show()
        self.thumb.content_set(ic)
        self.thumb.show()

        print("DEBUG: Changing song title")
        self.song.hide()
        self.song.text_set("Song: %s"%info['title'])
        self.song.show()

        print("DEBUG: Changing album title")
        self.album.hide()
        self.album.text_set("Album: %s"%info['album'])
        self.album.show()

        print("DEBUG: Changing artist")
        self.artist.hide()
        self.artist.text_set("<b><div align='center'>Artist: %s</div></b>"%info['artist'])
        self.artist.show()

        print("DEBUG: Changing clock to zero")
        self.counter[0].hide()
        self.counter[0].time_set(0, 0, 0)
        self.counter[0].show()

        print("DEBUG: Changing total time")
        self.counter[1].hide()
        mins, seconds = 0, 0
        while not mins and (seconds == 1 or seconds == 0):
            time.sleep(0.25)
            mins, seconds = self.ourPlayer.getSongDuration()
        if int(seconds) > 9:
            self.counter[1].text_set("<b>/      %s : %s</b>"%(mins, int(seconds)))
        else:
            self.counter[1].text_set("<b>/      %s : 0%s</b>"%(mins, int(seconds)))
        self.counter[1].show()

        print("DEBUG: Changing ratings")
        self.rating.hide()
        ic = elementary.Icon(self.mainWindow)
        rating = self.ourPlayer.getSongRating()
        if not rating:
            ic.file_set('images/favorite.png')
            self.rating.tooltip_text_set("Like Song")
        elif rating == 'love':
            ic.file_set('images/love.png')
            self.rating.tooltip_text_set("Song already liked")
        else:
            ic.file_set('images/ban.png')
        self.rating.content_set(ic)
        self.rating.show()

        print("DEBUG: Adding song to list")
        self.refreshInterface()

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
        if self.ourPlayer.player.play:
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
        print(("ctxpopup item selected: %s" % (item.text)))
        self.refreshInterface(True)
        self.ourPlayer.setStation(self.ourPlayer.getStationFromName(item.text))
        home = os.path.expanduser("~")
        if not os.path.exists("%s/.config/eAndora"%home):
            os.makedirs("%s/.config/eAndora"%home)
        if os.path.exists("%s/.config/eAndora/stationinfo"%home):
            os.remove('%s/.config/eAndora/stationinfo'%home)
        f = open('%s/.config/eAndora/stationinfo'%home, 'w')
        f.write('%s\n'%item.text)
        f.close()
        self.ourPlayer.pauseSong()
        self.ourPlayer.clearSongs()
        self.ourPlayer.addSongs()

    def refreshInterface( self, clear=False ):
        if clear:
            self.songList.clear()
        info = self.ourPlayer.getCurSongInfo()
        self.songList.item_prepend("%s - %s"%(info['title'], info['artist']))
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
        home = os.path.expanduser("~")
        if os.path.exists("%s/.config/eAndora/stationinfo"%home):
            f = open('%s/.config/eAndora/stationinfo'%home, 'r')
            lines = f.readlines()
            self.ourPlayer.setStation(self.ourPlayer.getStationFromName(lines[0].rstrip("\n")))
        else:
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

        self.stationButton.tooltip_text_set("Change Stations")
        self.stationButton.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.stationButton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.stationButton.callback_unpressed_add(self.station_selection)
        self.tb.pack(self.stationButton, 4, 0, 2, 3)

        self.songList.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.songList.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.songList, 0, 4, 4, 3)

        ic = elementary.Icon(self.mainWindow)
        ic.file_set("images/skip.png")
        bt = elementary.Button(self.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.skip_track)
        self.tb.pack(bt, 4, 4, 1, 1)
        bt.show()

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
        ic.file_set("images/ban.png")
        bt = elementary.Button(self.mainWindow)
        bt.tooltip_text_set("Ban Song")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.ban_track)
        self.tb.pack(bt, 5, 5, 1, 1)
        bt.show()

        #Define callbacks for all our buttons that will be updated
        #Button content is generated on song change

        self.thumb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.thumb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.thumb, 2, 0, 2, 3)

        self.song.callback_pressed_add(self.show_song)
        self.song.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.song.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.song, 0, 0, 2, 1)

        self.album.callback_pressed_add(self.show_album)
        self.album.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.album.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.album, 0, 1, 2, 1)

        self.rating.callback_unpressed_add(self.love_track)
        self.artist.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.artist.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.artist, 0, 2, 2, 1)

        self.counter[0].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.counter[0].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.counter[0].show_seconds_set(True)
        self.tb.pack(self.counter[0], 0, 3, 1, 1)

        self.counter[1].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.counter[1].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.counter[1], 2, 3, 1, 1)

        self.rating.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.rating.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.tb.pack(self.rating, 5, 4, 1, 1)

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

