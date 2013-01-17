import elementary
import evas

class createWindow(elementary.Box):
    def __init__( self, parent ):
        #builds a elementary box to accept login information
        elementary.Box.__init__(self, parent.mainWindow)

        self.ourPlayer = parent.ourPlayer
        self.win = parent.mainWindow
        self.rent = parent

        self.gl = gl = elementary.Genlist(self.win)
        gl.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        gl.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        gl.bounce_set(False, True)
        gl.show()

        sframe = elementary.Frame(self.win)
        sframe.text = "Search"
        sframe.size_hint_weight = (1.0, 0.0)
        sframe.size_hint_align = (-1.0, 0.0)
        search = elementary.Entry(self.win)
        search.single_line = True
        search.size_hint_weight = (1.0, 0.0)
        search.size_hint_align = (-1.0, 0.0)
        #search.callback_changed_add(self.populate_search)
        search.callback_activated_add(self.populate_search)

        stb = elementary.Button(self.win)
        stb.text = "Search"
        stb.callback_pressed_add(self.populate_search, search)

        sbox = elementary.Box(self.win)
        sbox.horizontal = True
        sbox.pack_end(search)
        sbox.pack_end(stb)

        sframe.content = sbox
        search.show()
        stb.show()
        sbox.show()
        sframe.show()

        self.create = create = elementary.Button(self.win)
        create.text_set("Create Station")
        create.callback_unpressed_add(self.create_station)
        create.show()

        ex = elementary.Button(self.win)
        ex.text_set("Back")
        ex.callback_unpressed_add(lambda x: parent.nf.item_pop())
        ex.show()

        bbox = elementary.Box(self.win)
        bbox.horizontal = True
        bbox.pack_end(create)
        bbox.pack_end(ex)
        bbox.show()

        self.pack_end(sframe)
        self.pack_end(gl)
        self.pack_end(bbox)

    def popup_message(self, message, title, callback=False):
        popup = elementary.Popup(self.win)
        popup.text = message
        popup.part_text_set("title,text", title)
        bt = elementary.Button(self.win)
        bt.text = "OK"
        if callback:
            bt.callback_clicked_add(callback, popup)
        bt.callback_clicked_add(lambda x: popup.hide())
        popup.part_content_set("button1", bt)
        popup.show()

    def create_station( self, bt):
        station = self.gl.selected_item_get()
        name = ""
        if station.data.resultType is 'song':
            name = "<b>%s</b> by %s"%(station.data.title, station.data.artist)
        elif station.data.resultType is 'artist':
            name = "<b>%s</b> (artist)"%(station.data.name)
        print name
        self.popup_message(name, "Station Created")
        self.ourPlayer.createStation(station.data.musicId)
        self.rent.nf.item_pop()

    def populate_search( self, bt, entry=False):
        self.gl.clear()
        if not entry:
            entry = bt

        itc = elementary.GenlistItemClass(item_style="default",
                                       content_get_func=self.item_return)

        results = self.ourPlayer.search(entry.text)
        for i in results:
            self.gl.item_append(itc, i, None)

    def item_return( self, obj, part, data ):
        if part == "elm.swallow.icon":
            lbl = elementary.Label(self.win)
            if data.resultType is 'song':
                lbl.text = "<b>%s</b> by %s"%(data.title, data.artist)
            elif data.resultType is 'artist':
                lbl.text = "<b>%s</b> (artist)"%(data.name)
            return lbl
        elif part == "elm.swallow.end":
            pass
        return None
