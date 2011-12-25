import gtk

class TrackView(gtk.TreeView):
    'The tracks tree view.'
    def __init__(self):
        super(TrackView, self).__init__(gtk.ListStore(int, str, str, str))
        
        renderer = gtk.CellRendererText()
        
        artist = gtk.TreeViewColumn('Artist', renderer, text=1)
        artist.set_resizable(True)
        artist.set_sort_column_id(1)
        self.append_column(artist)
        
        name = gtk.TreeViewColumn('Name', renderer, text=2)
        name.set_resizable(True)
        name.set_sort_column_id(2)
        self.append_column(name)
        
        release = gtk.TreeViewColumn('Release', renderer, text=3)
        release.set_resizable(True)
        release.set_sort_column_id(3)
        self.append_column(release)
        
        self.connect('cursor-changed', self.load_track)
                        
    def add_track(self, track):
        self.get_model().append((track.TrackID, track.Artist, track.Name, None))
        
    def load_track(self, view):
        model, it = self.get_selection().get_selected()
        tid, release = model.get_value(it, 0), model.get_value(it, 3)
        
        if not release:
            track = Window.instance.controller.get_track(tid)
            Window.instance.controller.get_release(track, self.load_track_callback, it)
        
    def load_track_callback(self, track, release, it):
        self.get_model().set_value(it, 3, release._id)
        Window.instance.status.set_status(str(release))

class PlaylistView(gtk.TreeView):
    'The playlists tree view.'
    def __init__(self):
        super(PlaylistView, self).__init__(gtk.ListStore(int, str))
                
        renderer = gtk.CellRendererText()
        
        name = gtk.TreeViewColumn('Playlists', renderer, text=1)
        name.set_sort_column_id(1)
        self.append_column(name)
        
        self.connect('cursor-changed', self.load_playlist)
                
    def add_playlist(self, playlist):
        self.get_model().append((playlist.PlaylistID, playlist.Name))
        
    def load_playlist(self, view):
        Window.instance.tracks.get_model().clear()

        model, it = self.get_selection().get_selected()
        plid = model.get_value(it, 0)
        
        playlist = Window.instance.controller.get_playlist(plid)
        
        for tid in playlist.Items:
            track = Window.instance.controller.get_track(tid)
            Window.instance.tracks.add_track(track)

class Status(gtk.HBox):
    'The status bar.'
    def __init__(self):
        super(Status, self).__init__()
              
        self.status = gtk.Label('')
        self.status.set_padding(2, 2)

        self.pack_start(self.status)
                                        
    def set_status(self, text):
        self.status.set_text(text)
         
class Window(gtk.Window):
    'The main window. We use a singleton pattern for convenience.'
    instance = None
    
    def __init__(self, controller):
        'Instantiates the main window.'
        super(Window, self).__init__(gtk.WINDOW_TOPLEVEL)
        
        self.controller = controller
        Window.instance = self
        
        self.set_title('iTunes-Discogs 1.0')
        
        self.connect('destroy', self.destroy)
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()

        self.playlists = PlaylistView()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(200, 600)
        scrollable.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.playlists)
        hbox.pack_start(scrollable, False)
        
        separator = gtk.VSeparator()
        hbox.pack_start(separator, False)
        
        self.tracks = TrackView()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(600, 600)
        scrollable.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.tracks)
        hbox.pack_end(scrollable)
        
        vbox.pack_start(hbox)
        vbox.pack_start(gtk.HSeparator())
        
        self.status = Status()
        vbox.pack_end(self.status, False)
        
        self.add(vbox)
        
        for playlist in self.controller.get_playlists().values():
            self.playlists.add_playlist(playlist)
        
        self.show_all()
        gtk.main()
        
    def destroy(self, widget, data=None):
        Window.instance = None
        gtk.main_quit()
        