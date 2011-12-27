from config import Field
from itunes import Playlist
import config
import gtk
import pango
    
class Menu(gtk.MenuBar):
    'The main menu bar.'
    def __init__(self):
        super(Menu, self).__init__()
        
        menu = gtk.Menu()
        
        item = gtk.MenuItem('Preferences')
        item.connect('activate', Window.instance.preferences.show_all)
        
        menu.append(item)
        
        item = gtk.MenuItem('Quit')
        item.connect('activate', Window.instance.destroy)
        
        menu.append(item)
        
        item = gtk.MenuItem(config.NAME)
        item.set_submenu(menu)
        
        self.add(item)
        
        menu = gtk.Menu()
        
        item = gtk.MenuItem('About')
        item.connect('activate', Window.instance.about.show_all)
        
        menu.append(item)
        
        item = gtk.MenuItem('Help')
        item.set_submenu(menu)
        
        self.add(item)
        
class About(gtk.AboutDialog):
    'The about dialog.'
    def __init__(self):
        super(About, self).__init__()
        
        self.set_name(config.NAME)
        self.set_version(config.VERSION)
        
        self.set_authors(['Jay Dolan'])
        
    def show_all(self, event):
        super(About, self).show_all()
        
class Preferences(gtk.Dialog):
    'The preferences dialog.'
    class Fields(gtk.TreeView):
        'The fields view.'
        def __init__(self):
            super(Preferences.Fields, self).__init__(gtk.ListStore(str, str, str, str))
            self.modify_font(pango.FontDescription('8'))
            self.set_rules_hint(True)
            self.set_size_request(600, 280)
                        
            field = gtk.TreeViewColumn('Field', gtk.CellRendererText(), text=0)
            self.append_column(field)
            
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', True)
            
            source = gtk.TreeViewColumn('Source', renderer, text=1)
            self.append_column(source)
            
            target = gtk.TreeViewColumn('Target', renderer, text=2)
            self.append_column(target)
        
            actions = gtk.ListStore(str)
            for action in Field.actions:
                actions.append((action,))
            
            combo = gtk.CellRendererCombo()
            combo.set_property('editable', True)
            combo.set_property('has-entry', False)
            combo.set_property('model', actions)
            combo.set_property('text-column', 0)
            
            action = gtk.TreeViewColumn('Action', combo, text=3)
            self.append_column(action)
            
            for field in Window.instance.controller.config.fields:
                row = (field.name, field.source, field.target, field.action)
                self.get_model().append(row)
        
    def __init__(self):
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        super(Preferences, self).__init__('Preferences', Window.instance, flags, buttons)
        
        self.vbox.set_size_request(600, 300)
        
        notebook = gtk.Notebook()        
        notebook.set_tab_pos(gtk.POS_TOP)
        
        box = gtk.HBox()
        
        notebook.append_page(box, gtk.Label('General'))
        
        box = gtk.HBox()
        
        self.fields = Preferences.Fields()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.fields)
        
        box.pack_start(scrollable)    
        
        notebook.append_page(box, gtk.Label('Fields'))
        
        self.vbox.add(notebook)
        
        self.connect('response', self.response)
        
    def show_all(self, event=None):
        super(Preferences, self).show_all()
        
    def response(self, dialog, response):
        if response == gtk.RESPONSE_OK:
            it = self.fields.get_model().get_iter_first()
            print it
        self.hide()
         
class Window(gtk.Window):
    'The main window. We use a singleton pattern for convenience.'
    instance = None
    
    class Playlists(gtk.TreeView):
        'The playlists tree view.'
        def __init__(self):
            super(Window.Playlists, self).__init__(gtk.ListStore(int, str))
            self.modify_font(pango.FontDescription('8'))
            
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
                       
    class Tracks(gtk.TreeView):
        'The tracks tree view.'
        def __init__(self):
            super(Window.Tracks, self).__init__(gtk.ListStore(int, str, str, str))
            self.modify_font(pango.FontDescription('8'))
            self.set_rules_hint(True)
            
            renderer = gtk.CellRendererText()
            
            artist = gtk.TreeViewColumn('Artist', renderer, text=1)
            artist.set_min_width(200)
            artist.set_resizable(True)
            artist.set_sort_column_id(1)
            self.append_column(artist)
            
            name = gtk.TreeViewColumn('Name', renderer, text=2)
            name.set_min_width(200)
            name.set_resizable(True)
            name.set_sort_column_id(2)
            self.append_column(name)
            
            renderer = gtk.CellRendererText()
            renderer.set_property('foreground', 'blue')
            renderer.set_property('underline', pango.UNDERLINE_SINGLE)
            
            release = gtk.TreeViewColumn('Release', renderer, text=3)
            release.set_min_width(200)
            release.set_resizable(True)
            release.set_sort_column_id(3)
            self.append_column(release)
            
            self.connect('cursor-changed', self.load_track)
                            
        def add_track(self, track):
            rel = None
            if track.release:
                rel = str(track.release)
            self.get_model().append((track.TrackID, track.Artist, track.Name, rel))
            
        def load_track(self, view):
            model, it = self.get_selection().get_selected()
            tid, release = model.get_value(it, 0), model.get_value(it, 3)
            
            if not release:
                track = Window.instance.controller.get_track(tid)
                Window.instance.controller.get_release(track, self.load_track_callback, it)
            
        def load_track_callback(self, track, release, it):
            if not release:
                return
            self.get_model().set_value(it, 3, str(release))
            Window.instance.status.set_status(str(release))
    
    class Status(gtk.HBox):
        'The status bar.'
        def __init__(self):
            super(Window.Status, self).__init__()
                  
            self.status = gtk.Label('')
            self.status.set_padding(2, 2)
    
            self.pack_start(self.status)
                                            
        def set_status(self, text):
            self.status.set_text(text)
    
    def __init__(self, controller):
        'Instantiates the main window.'
        super(Window, self).__init__(gtk.WINDOW_TOPLEVEL)
                
        self.controller = controller
        Window.instance = self
        
        self.set_title(config.NAME)
        
        self.connect('destroy', self.destroy)
        
        self.about = About()
        self.preferences = Preferences()

        vbox = gtk.VBox()
        hbox = gtk.HBox()
        
        self.menu = Menu()
        vbox.pack_start(self.menu, False)        

        self.playlists = Window.Playlists()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(200, 600)
        scrollable.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.playlists)
        hbox.pack_start(scrollable, False)
        
        separator = gtk.VSeparator()
        hbox.pack_start(separator, False)
        
        self.tracks = Window.Tracks()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(800, 600)
        scrollable.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.tracks)
        hbox.pack_end(scrollable)
        
        vbox.pack_start(hbox)
        vbox.pack_start(gtk.HSeparator())
        
        self.status = Window.Status()
        vbox.pack_end(self.status, False)
        
        self.add(vbox)
        
        playlists = set(self.controller.get_playlists().values())
        for playlist in sorted(playlists, Playlist.compare):
            self.playlists.add_playlist(playlist)
        
        self.show_all()
        gtk.main()
        
    def destroy(self, widget, data=None):
        Window.instance = None
        gtk.main_quit()
        