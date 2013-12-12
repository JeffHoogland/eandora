import elementary
import evas

class loginWindow(elementary.Box):
    def __init__( self, parent ):
        #builds a elementary box to accept login information
        elementary.Box.__init__(self, parent.mainWindow)

        eframe = elementary.Frame(parent.mainWindow)
        eframe.text_set("Email:")
        eframe.size_hint_weight_set(1, 1)
        eframe.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        eframe.show()

        log = elementary.Entry(parent.mainWindow)
        log.single_line = True
        log.input_panel_return_key_disabled_set(True)
        log.size_hint_weight_set(1, 1)
        log.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        eframe.content = log
        log.show()

        pframe = elementary.Frame(parent.mainWindow)
        pframe.text_set("Password:")
        pframe.size_hint_weight_set(1, 1)
        pframe.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        pframe.show()

        ck = elementary.Check(parent.mainWindow)
        ck.text_set("Store Login")
        self.pack_end(ck)
        ck.show()

        pas = elementary.Entry(parent.mainWindow)
        pas.single_line = True
        pas.line_wrap_set(False)
        pas.password = True
        pas.input_panel_return_key_disabled = True
        pas.size_hint_weight_set(1, 1)
        pas.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        pframe.content = pas
        pas.show()

        lg = elementary.Button(parent.mainWindow)
        lg.text_set("Login")
        lg.size_hint_weight_set(.25, .25)
        lg.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        lg.callback_unpressed_add(parent.login_user, log, pas, parent.mainWindow, ck)
        lg.show()

        ex = elementary.Button(parent.mainWindow)
        ex.text_set("Exit")
        ex.size_hint_weight_set(.25, .25)
        ex.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        ex.callback_unpressed_add(lambda o: elementary.exit())
        ex.show()

        self.pack_end(eframe)
        self.pack_end(pframe)
        self.pack_end(ck)
        self.pack_end(lg)
        self.pack_end(ex)
