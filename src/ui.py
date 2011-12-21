import gtk

class TrackView(gtk.TreeView):
    'The tracks tree view.'
    def __init__(self):
        super(TrackView, self).__init__(gtk.ListStore(int, str, str))
        
        renderer = gtk.CellRendererText()
        
        artist = gtk.TreeViewColumn('Artist', renderer, text=1)
        self.append_column(artist)
        
        name = gtk.TreeViewColumn('Name', renderer, text=2)
        self.append_column(name)
                        
    def add(self, track):
        self.get_model().append((track.TrackID, track.Artist, track.Name))

class PlaylistView(gtk.TreeView):
    'The playlists tree view.'
    def __init__(self):
        super(PlaylistView, self).__init__(gtk.ListStore(int, str))
        
        self.connect('cursor-changed', self.load)
        
        renderer = gtk.CellRendererText()
        
        name = gtk.TreeViewColumn('Playlists', renderer, text=1)
        self.append_column(name)
        
        playlists = Window.instance.controller.library.playlists
        for playlist in playlists.values():
            self.add(playlist)
                
    def add(self, playlist):
        self.get_model().append((playlist.PlaylistID, playlist.Name))
        
    def load(self, tree_view):
        Window.instance.tracks.get_model().clear()

        model, it = self.get_selection().get_selected()
        plid = model.get_value(it, 0)
        
        playlist = Window.instance.controller.get_playlist(plid)
        
        for tid in playlist.Items:
            track = Window.instance.controller.get_track(tid)
            Window.instance.tracks.add(track)
     
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
        scrollable.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollable.add_with_viewport(self.playlists)
        hbox.pack_start(scrollable, False)
        
        self.tracks = TrackView()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(600, 600)
        scrollable.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollable.add_with_viewport(self.tracks)
        hbox.pack_end(scrollable)
        
        vbox.pack_start(hbox)
        self.add(vbox)
        
        self.show_all()
        gtk.main()
        
    def destroy(self, widget, data=None):
        Window.instance = None
        gtk.main_quit()
        