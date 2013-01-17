import elementary
import evas
import os

class renameWindow(elementary.Box):
    def __init__( self, parent, name ):
        #builds a elementary box to accept login information
        elementary.Box.__init__(self, parent.mainWindow)

        self.ourPlayer = parent.ourPlayer
        self.win = parent.mainWindow
        self.rent = parent
        self.nerm = name

        frame = elementary.Frame(self.win)
        frame.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        frame.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        frame.text = "New Name for %s"%name

        self.entry = entry = elementary.Entry(self.win)
        entry.single_line = True
        entry.callback_activated_add(self.change_name)

        frame.content = entry
        entry.show()
        frame.show()

        chng = elementary.Button(self.win)
        chng.text_set("Change Name")
        chng.callback_unpressed_add(self.change_name)
        chng.callback_unpressed_add(lambda x: parent.nf.item_pop())
        chng.show()

        ex = elementary.Button(self.win)
        ex.text_set("Cancel")
        ex.callback_unpressed_add(lambda x: parent.nf.item_pop())
        ex.show()

        bbox = elementary.Box(self.win)
        bbox.horizontal = True
        bbox.pack_end(chng)
        bbox.pack_end(ex)
        bbox.show()

        self.pack_end(frame)
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

    def change_name(self, toss=False, toss2=False):
        self.ourPlayer.renameStation(self.ourPlayer.getStationFromName(self.nerm), self.entry.text)
