import vlc
import pandora
import webbrowser
import urllib

Download = False
DownloadPath = "/media/sda5/Music/pandora/"

def openBrowser(url):
    print "Opening %s"%url
    webbrowser.open(url)
    try:
        os.wait() # workaround for http://bugs.python.org/issue5993
    except:
        pass

class eAndora(object):
    def __init__( self, parent ):
        self.gui = ""
        self.rent = parent
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
        self.displaysongs = []
        self.songCount = 0

    def setGUI( self, GUI):
        self.gui = GUI
        self.player = vlc.MediaPlayer()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,      self.nextSong)

    def auth( self, user, passwd):
        print "User %s - Password %s"%(user, passwd)
        self.settings['username'] = user
        self.settings['password'] = passwd
        try:
            self.pandora.connect(self.settings['username'], self.settings['password'])
        except:
            self.rent.login_error()

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
        print "Getting Song duration"
        seconds = self.player.get_length() / 1000.0
        print "Starting Seconds %s"%seconds
        mins = 0
        while seconds >= 60:
            seconds -= 60
            mins += 1
        print "Minutes %s Seconds %s"%(mins, seconds) 
        return mins, seconds

    def getSongRating( self ):
        return self.songinfo[self.curSong]['rating']

    def search( self, searchstring ):
        return self.pandora.search(searchstring)

    def createStation( self, station ):
        self.pandora.add_station_by_music_id(station)

    def deleteStation( self, station ):
        pandora.Station(self.pandora, station).delete()

    def renameStation( self, station, name ):
        pandora.Station(self.pandora, station).rename(name)

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

    def check_download( self, url, title ):
        if Download:
            urllib.urlretrieve(str(url), '%s%s.mp3'%(DownloadPath, title))

    def nextSong( self , event=False ):
        print("Debug 1")
        if self.player.is_playing():
            self.player.stop()
        print("Debug 2")
        self.player = vlc.MediaPlayer()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,      self.nextSong)
        print("Debug 3")
        self.curSong += 1
        info = self.songinfo[self.curSong]
        self.displaysongs.append(info)
        self.song = info['title']
        print(info)
        print("Debug 4")
        self.player.set_media(vlc.Media(info['url']))
        print("Debug 5")
        self.playing = True
        self.player.play()
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

