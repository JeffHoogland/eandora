import elementary
import evas
import os

class stationWindow(elementary.Box):
    def __init__( self, parent ):
        #builds a elementary box to accept login information
        elementary.Box.__init__(self, parent.mainWindow)

        self.ourPlayer = parent.ourPlayer
        self.win = parent.mainWindow
        self.rent = parent

        self.lst = lst = elementary.List(self.win)
        lst.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        lst.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        lst.callback_clicked_double_add(self.station_popup)
        lst.callback_longpressed_add(self.station_popup)
        stations = self.ourPlayer.getStations()
        for station in stations:
            lst.item_append(str(station['stationName']))
        lst.show()

        chng = elementary.Button(self.win)
        chng.text_set("Change Station")
        chng.callback_unpressed_add(self.change_station)
        chng.show()

        sep = elementary.Separator(self.win)
        sep.show()

        crt = elementary.Button(self.win)
        crt.text = "Create Station"
        crt.callback_unpressed_add(lambda x: parent.spawn_create())
        crt.show()

        ex = elementary.Button(self.win)
        ex.text_set("Back")
        ex.callback_unpressed_add(lambda x: parent.nf.item_pop())
        ex.show()

        bbox = elementary.Box(self.win)
        bbox.horizontal = True
        bbox.pack_end(chng)
        bbox.pack_end(sep)
        bbox.pack_end(crt)
        bbox.pack_end(sep)
        bbox.pack_end(ex)
        bbox.show()

        self.pack_end(lst)
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

    def station_popup(self, lst, item):
        print lst
        print item.text
        cp = elementary.Ctxpopup(self.win)
        cp.item_append("Play", None, self.change_station)
        cp.item_append("Rename", None, self.station_rename)
        cp.item_append("Delete", None, self.station_delete)
        pos = self.win.evas.pointer_canvas_xy_get()
        cp.pos = pos
        cp.show()

    def station_rename(self, lst, i):
        cp = i.widget_get()
        cp.dismiss()
        item = self.lst.selected_item_get()
        self.rent.spawn_rename(item.text)

    def station_delete(self, lst, i):
        cp = i.widget_get()
        cp.dismiss()
        item = self.lst.selected_item_get()
        print item.text

        popup = elementary.Popup(self.win)
        popup.text = item.text
        popup.part_text_set("title,text", "Really Delete?")
        bt = elementary.Button(self.win)
        bt.text = "Cancel"
        bt.callback_clicked_add(lambda x: popup.hide())
        ys = elementary.Button(self.win)
        ys.text = "Yes"
        ys.callback_clicked_add(self.really_delete, item.text)
        ys.callback_clicked_add(lambda x: popup.hide())
        popup.part_content_set("button1", bt)
        popup.part_content_set("button2", ys)
        popup.show()

    def really_delete(self, pop, name):
        station = self.ourPlayer.getStationFromName(name)
        print station
        self.ourPlayer.deleteStation(station)
        self.rent.nf.item_pop()
        
    def change_station(self, bt=False, i=False):
        if i:
            cp = i.widget_get()
            cp.dismiss()
        item = self.lst.selected_item_get()
        #self.rent.spawn_player()
        if item:
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
            self.ourPlayer.gui.refreshInterface(True)
            self.rent.nf.item_pop()
