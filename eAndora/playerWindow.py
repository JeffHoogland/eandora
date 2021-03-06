import elementary
import evas
import ecore
import urllib
import time
import os
import shutil
import datetime

class playerWindow(elementary.Box):
    def __init__( self, parent ):
        #Builds an elementary tabel that displays our information
        elementary.Box.__init__(self, parent.mainWindow)

        #Store the global window
        self.win = parent.mainWindow

        #Store our parent window
        self.rent = parent

        #Access the player function we need to talk to
        self.ourPlayer = parent.ourPlayer
        self.ourPlayer.setGUI(self)

        #Internal length of our current song
        self.duration = 0.0

        #These are widgets that appear at the player page of our window
        self.songList = elementary.List(parent.mainWindow)
        self.stationButton = elementary.Label(parent.mainWindow)
        self.thumb = elementary.Button(parent.mainWindow)
        self.song = elementary.Button(parent.mainWindow)
        self.artist = elementary.Label(parent.mainWindow)
        self.album = elementary.Button(parent.mainWindow)
        self.rating = elementary.Button(parent.mainWindow)
        self.menubutton = elementary.Toolbar(parent.mainWindow)
        self.mainmenu = elementary.Menu(parent.mainWindow)
        #self.counter = [elementary.Clock(parent.mainWindow), elementary.Label(parent.mainWindow), elementary.Label(parent.mainWindow)]
        self.counter = SeekControls(parent)
        self.pauseTime = None

        self.playtimer = playtimer = ecore.timer_add(0.2, self.update)
        playtimer.freeze()

        #Build the page layout
        home = os.path.expanduser("~")
        if os.path.exists("%s/.config/eAndora/stationinfo"%home):
            f = open('%s/.config/eAndora/stationinfo'%home, 'r')
            lines = f.readlines()
            self.ourPlayer.setStation(self.ourPlayer.getStationFromName(lines[0].rstrip("\n")))
        else:
            self.ourPlayer.setStation(self.ourPlayer.getStations()[0])

        self.songList.size_hint_weight_set(2, 2)
        self.songList.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        #Our main menu
        self.menubutton.size_hint_weight_set(evas.EVAS_HINT_EXPAND/4, evas.EVAS_HINT_EXPAND/4)
        self.menubutton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        item = self.menubutton.item_append("%s/images/eAndora.png"%self.rent.location, "Menu", None, None)
        item.menu_set(True)
        self.menubutton.menu_parent_set(parent.mainWindow)
        menu = item.menu_get()
        menu.item_add(None, "About", "%s/images/about.png"%self.rent.location, self.about)
        menu.item_add(None, "Stations", "%s/images/search.png"%self.rent.location, self.stations)
        #menu.item_add(None, "Settings", "%s/images/settings.png", self.settings)
        menu.item_add(None, "Logout", "refresh", self.logout)
        menu.item_add(None, "Exit", "%s/images/exit.png"%self.rent.location, self.exit)
        self.menubutton.show()

        ic = elementary.Icon(parent.mainWindow)
        ic.file_set("%s/images/skip.png"%self.rent.location)
        skip = elementary.Button(parent.mainWindow)
        skip.size_hint_weight_set(1, 1)
        skip.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        skip.content_set(ic)
        skip.tooltip_text_set("Skip Song")
        skip.callback_unpressed_add(self.skip_track)
        skip.show()

        ic = elementary.Icon(parent.mainWindow)
        ic.file_set("%s/images/pause.png"%self.rent.location)
        pp = elementary.Button(parent.mainWindow)
        pp.size_hint_weight_set(1, 1)
        pp.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        pp.content_set(ic)
        pp.tooltip_text_set("Pause Song")
        pp.callback_unpressed_add(self.play_pause)
        pp.show()

        ic = elementary.Icon(parent.mainWindow)
        ic.file_set("%s/images/ban.png"%self.rent.location)
        ban = elementary.Button(parent.mainWindow)
        ban.tooltip_text_set("Ban Song")
        ban.size_hint_weight_set(1, 1)
        ban.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        ban.content_set(ic)
        ban.callback_unpressed_add(self.ban_track)
        ban.show()

        #Define callbacks for all our buttons that will be updated
        #Button content is generated on song change

        self.thumb.size_hint_weight_set(1, 1)
        self.thumb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.song.callback_pressed_add(self.show_song)
        self.song.size_hint_weight_set(.25, .25)
        self.song.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.album.callback_pressed_add(self.show_album)
        self.album.size_hint_weight_set(.25, .25)
        self.album.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.rating.callback_unpressed_add(self.love_track)
        self.artist.size_hint_weight_set(.25, .25)
        self.artist.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.stationButton.size_hint_weight_set(.25, .25)
        self.stationButton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.counter.size_hint_weight_set(1, 1)
        self.counter.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.rating.size_hint_weight_set(1, 1)
        self.rating.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        #Position of all the items on the table
        self.pack_end(self.song)
        self.pack_end(self.album)
        self.pack_end(self.artist)
        self.pack_end(self.stationButton)

        mybox = elementary.Box(self.win)
        mybox.horizontal = True
        mybox.size_hint_weight_set(1, 1)
        mybox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        mybox.pack_end(self.thumb)
        mybox.pack_end(self.menubutton)
        mybox.show()
        self.pack_end(mybox)

        thbox = elementary.Box(self.win)
        thbox.horizontal = True
        thbox.size_hint_weight_set(.5, .5)
        thbox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        thbox.pack_end(pp)
        thbox.pack_end(skip)
        thbox.pack_end(self.rating)
        thbox.pack_end(ban)
        thbox.show()
        self.pack_end(thbox)

        self.pack_end(self.counter)
        self.pack_end(self.songList)

        self.ourPlayer.addSongs()

    def update(self):
        if self.rent.backend == "vlc":
            pos = self.ourPlayer.player.get_time() / 1000.0
        else:
            pos = self.ourPlayer.player.position_get()

        pos = datetime.timedelta(seconds=int(pos))
        self.position = pos
        t = "<b><div align='center'>%s  /  %s</div></b>" % (pos, self.duration)
        self.counter.text_set(t)

        if self.rent.backend == "vlc":
            dur = self.ourPlayer.player.get_length() / 1000.0
        else:
            dur = self.ourPlayer.player.play_length

        if dur != self.duration:
            dur = datetime.timedelta(seconds=int(dur))
            self.duration = dur

        return 1

    def ban_track( self, bt ):
        #Tell pandora we don't want this song played anymore, then skip to the next track
        self.ourPlayer.banSong()
        self.ourPlayer.skipSong()

    def love_track( self, bt ):
        #Tell pandora we love this song, then update the GUI so it reflects this change
        self.ourPlayer.loveSong()
        ic = elementary.Icon(self.rent.mainWindow)
        ic.file_set('%s/images/love.png'%self.rent.location)
        self.rating.hide()
        self.rating.tooltip_text_set("Song already liked")
        self.rating.content_set(ic)
        self.rating.show()

    def show_song( self, bt ):
        #Opens song information in the user's default web browser
        self.ourPlayer.showSong()

    def show_album( self, bt ):
        #Opens album information in the user's default web browser
        self.ourPlayer.showAlbum()

    def song_change( self ):
        #Updates the GUI so it reflects a new song's infromation
        info = self.ourPlayer.getCurSongInfo()
        print("DEBUG: Changing Album Art")
        try:
            os.remove('/tmp/albumart.jpg')
        except:
            pass
        urllib.urlretrieve(str(info['thumbnail']), '/tmp/albumart.jpg')
        ic = elementary.Icon(self.rent.mainWindow)
        ic.file_set('/tmp/albumart.jpg')
        self.thumb.hide()
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

        self.playtimer.thaw()

        print("DEBUG: Changing ratings")
        self.rating.hide()
        ic = elementary.Icon(self.rent.mainWindow)
        rating = self.ourPlayer.getSongRating()
        if not rating:
            ic.file_set('%s/images/favorite.png'%self.rent.location)
            self.rating.tooltip_text_set("Like Song")
        elif rating == 'love':
            ic.file_set('%s/images/love.png'%self.rent.location)
            self.rating.tooltip_text_set("Song already liked")
        else:
            ic.file_set('%s/images/ban.png'%self.rent.location)
        self.rating.content_set(ic)
        self.rating.show()

        print("DEBUG: Adding song to list")
        self.refreshInterface()

        print("Hey look the song changed!")

    def play_pause(self, bt):
        ic = elementary.Icon(self.rent.mainWindow)
        if self.rent.backend == "vlc":
            if self.ourPlayer.playing:
                ic.file_set("%s/images/play.png"%self.rent.location)
                self.playtimer.freeze()
                self.ourPlayer.pauseSong()
                bt.tooltip_text_set("Play Song")
            else:
                ic.file_set("%s/images/pause.png"%self.rent.location)
                self.playtimer.thaw()
                self.ourPlayer.playSong()
                bt.tooltip_text_set("Pause Song")

        else:
            if self.ourPlayer.player.play:
                ic.file_set("%s/images/play.png"%self.rent.location)
                self.playtimer.freeze()
                self.ourPlayer.pauseSong()
                bt.tooltip_text_set("Play Song")
            else:
                ic.file_set("%s/images/pause.png"%self.rent.location)
                self.playtimer.thaw()
                self.ourPlayer.playSong()
                bt.tooltip_text_set("Pause Song")
        bt.content_set(ic)
        bt.show()

    def skip_track(self, bt):
        self.ourPlayer.skipSong()

    def refreshInterface( self, clear=False ):
        if clear:
            self.songList.clear()
        info = self.ourPlayer.getCurSongInfo()
        self.songList.item_prepend("%s - %s"%(info['title'], info['artist']))
        self.songList.show()
        self.songList.go()
        self.stationButton.text_set("<b><div align='center'>Station: %s</div></b>"%str(self.ourPlayer.getStation().name))
        self.stationButton.hide()
        self.stationButton.show()

    def station_selection(self, bt):
        self.rent.spawn_stations()

    def about(self, menu, item):
        popup = elementary.Popup(self.win)
        popup.text = "Pandora Internet Radio player written in python and elementary. Streaming backend: %s By: Jeff Hoogland" %self.rent.backend
        popup.part_text_set("title,text", "About")
        bt = elementary.Button(self.win)
        bt.text = "Close"
        bt.callback_clicked_add(lambda x: popup.delete())
        popup.part_content_set("button1", bt)
        popup.show()

    def stations(self, menu, item):
        self.rent.spawn_stations()

    def settings(self, menu, item):
        self.rent.spawn_settings()

    def logout(self, menu, item):
        print "Log out"
        self.ourPlayer.pauseSong()
        self.ourPlayer.clearSongs()
        home = os.path.expanduser("~")
        shutil.rmtree('%s/.config/eAndora'%home)
        self.rent.spawn_login()

    def exit(self, menu, item):
        elementary.exit()

class SeekControls(elementary.Label):
    def __init__(self, parent):
        window = parent.mainWindow
        elementary.Label.__init__(self, window)

        self.text_set("00:00  /  00:00")
        self.show()

        self.size_hint_weight_set(1, 1)
        self.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.show()
