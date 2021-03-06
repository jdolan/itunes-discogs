from config import Field
from itunes import Playlist
import async
import config
import gtk
import pango
        
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
                        
            column = gtk.TreeViewColumn('Field', gtk.CellRendererText(), text=0)
            self.append_column(column)
            
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', True)
            renderer.connect('edited', self.edit, 1)
            
            column = gtk.TreeViewColumn('Source', renderer, text=1)
            self.append_column(column)
            
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', True)
            renderer.connect('edited', self.edit, 2)
            
            column = gtk.TreeViewColumn('Target', renderer, text=2)
            self.append_column(column)
        
            actions = gtk.ListStore(str)
            for action in Field.actions:
                actions.append((action,))
            
            renderer = gtk.CellRendererCombo()
            renderer.set_property('editable', True)
            renderer.set_property('has-entry', False)
            renderer.set_property('model', actions)
            renderer.set_property('text-column', 0)
            renderer.connect('edited', self.edit, 3)
                        
            column = gtk.TreeViewColumn('Action', renderer, text=3)
            self.append_column(column)
            
            self.set_fields()
            
        def edit(self, renderer, row, text, column):
            self.get_model()[row][column] = text
             
        def get_fields(self):
            return [Field(row[0], row[1], row[2], row[3]) for row in self.get_model()]
        
        def set_fields(self):
            self.get_model().clear()
            for field in Window.instance.controller.config.fields:
                self.get_model().append((field.name, field.source, field.target, field.action))
        
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
            config = Window.instance.controller.config
            config.fields = self.fields.get_fields()
            
        self.hide()
         
class Window(gtk.Window):
    'The main window. We use a singleton pattern for convenience.'
    instance = None
    
    class Menu(gtk.MenuBar):
        'The main menu bar.'
        def __init__(self):
            super(Window.Menu, self).__init__()
            
            menu = gtk.Menu()
            
            item = gtk.MenuItem('_Preferences')
            item.connect('activate', Window.instance.preferences.show_all)
            
            menu.append(item)
            
            item = gtk.MenuItem('_Quit')
            item.connect('activate', Window.instance.destroy)
            
            menu.append(item)
            
            item = gtk.MenuItem(config.NAME)
            item.set_submenu(menu)
            
            self.add(item)
            
            menu = gtk.Menu()
            
            item = gtk.MenuItem('_About')
            item.connect('activate', Window.instance.about.show_all)
            
            menu.append(item)
            
            item = gtk.MenuItem('Help')
            item.set_submenu(menu)
            
            self.add(item)
            
    class Controls(gtk.HBox):
        'The primary control buttons.'
        def __init__(self):
            super(Window.Controls, self).__init__()
                        
            self.search_button = gtk.Button('_Find', gtk.STOCK_FIND)
            self.search_button.set_size_request(64, 48)
            self.search_button.set_image_position(gtk.POS_TOP)
            self.pack_start(self.search_button, False)
            
            self.search_button.connect('clicked', self.search)
            
            self.cancel_button = gtk.Button('Cancel', gtk.STOCK_CANCEL)
            self.cancel_button.set_size_request(64, 48)
            self.cancel_button.set_image_position(gtk.POS_TOP)
            self.pack_start(self.cancel_button, False)
            
            self.cancel_button.connect('clicked', self.cancel)
            
        def search(self, button):
            'Resolve search results for the selected tracks.'
            model, rows = Window.instance.tracks.get_selection().get_selected_rows()
            if not rows:
                rows = range(0, len(model))
                
            controller = Window.instance.controller
            
            for row in rows:
                track = controller.get_track(model[row][0])
                if not track.release:
                    async.run(controller.search, (track,), self.search_cb, (model, row))
        
        def search_cb(self, track, data):
            'A release will be set for successful searches.'
            (model, row) = data
            if track.release:
                model[row][3] = str(track.release)
            else:
                model[row][3] = 'Not found'
                
            Window.instance.status.set_status('Processed %s' % track)
            
        def cancel(self, button):
            'Cancel any pending work.'
            while not async.queue.empty():
                async.queue.get()
    
    class Playlists(gtk.TreeView):
        'The playlists tree view.'
        def __init__(self):
            super(Window.Playlists, self).__init__(gtk.ListStore(int, str))
            
            self.modify_font(pango.FontDescription('8'))
                        
            column = gtk.TreeViewColumn('Playlists', gtk.CellRendererText(), text=1)
            self.append_column(column)
            
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
            
            self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)            
            
            renderer = gtk.CellRendererText()
            
            column = gtk.TreeViewColumn('Artist', renderer, text=1)
            column.set_min_width(200)
            column.set_resizable(True)
            column.set_sort_column_id(1)
            self.append_column(column)
            
            column = gtk.TreeViewColumn('Name', renderer, text=2)
            column.set_min_width(200)
            column.set_resizable(True)
            column.set_sort_column_id(2)
            self.append_column(column)
            
            renderer = gtk.CellRendererCombo()
            renderer.set_property('foreground', 'blue')
            renderer.set_property('underline', pango.UNDERLINE_SINGLE)
            renderer.set_property('editable', True)
            renderer.set_property('has-entry', False)
            renderer.set_property('model', gtk.ListStore(int, str))
            renderer.set_property('text-column', 1)
            renderer.connect('editing-started', self.show_results)
            renderer.connect('changed', self.select_result)            
            
            column = gtk.TreeViewColumn('Release', renderer, text=3)
            column.set_min_width(200)
            column.set_resizable(True)
            self.append_column(column)
                                                    
        def add_track(self, track):
            'Append a track to the tree model.'
            release = None
            if track.release:
                release = str(track.release)
            self.get_model().append((track.TrackID, track.Artist, track.Name, release))
            
        def show_results(self, renderer, editable, path):
            'The user wishes to see search results. Populate the the drop-down.'
            tid = self.get_model()[path][0]
            track = Window.instance.controller.get_track(tid)
            
            renderer = self.get_column(2).get_cell_renderers()[0]
            
            model = renderer.get_property('model')
            model.clear()
            
            if track.search:
                i = 0
                for result in track.search.raw_results:
                    model.append((i, str(result)))
                    i += 1
                                
        def select_result(self, renderer, path, it):
            'A search result was selected. Resolve the release.'
            controller = Window.instance.controller
            
            tid = self.get_model()[path][0]
            track = controller.get_track(tid)
            
            model = renderer.get_property('model')
            i = model.get_value(it, 0)
            result = track.search.raw_results[i]
            
            async.run(controller.set_release, (track, result), self.select_result_cb, path)
    
        def select_result_cb(self, track, result, path):
            'Update the release information for the track.'
            if track.release:
                self.get_model()[path][3] = str(track.release)
                
    class Status(gtk.HBox):
        'The status bar.'
        def __init__(self):
            super(Window.Status, self).__init__()
            
            self.status = gtk.Label('')
            self.pack_start(self.status)
            
            self.progress = gtk.ProgressBar()
            self.progress.set_size_request(250, 16)
            self.pack_end(self.progress, False, padding=16)
                                            
        def set_status(self, text):
            self.status.set_text(text)
            
        def set_progress(self, frac):
            self.progress.set_fraction(frac)
    
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
        
        self.menu = Window.Menu()
        vbox.pack_start(self.menu, False)
        
        self.controls = Window.Controls()
        vbox.pack_start(self.controls, False)
        
        hbox.pack_start(gtk.VSeparator(), False)

        self.playlists = Window.Playlists()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(200, 600)
        scrollable.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.playlists)
        hbox.pack_start(scrollable, False)
        
        hbox.pack_start(gtk.VSeparator(), False)
        
        self.tracks = Window.Tracks()
        
        scrollable = gtk.ScrolledWindow()
        scrollable.set_size_request(800, 600)
        scrollable.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollable.add(self.tracks)
        hbox.pack_end(scrollable)
        
        vbox.pack_start(hbox)
        vbox.pack_start(gtk.HSeparator(), False)
        
        self.status = Window.Status()
        vbox.pack_end(self.status, False, padding=1)
        
        self.add(vbox)
        
        self.show_all()

        playlists = set(self.controller.get_playlists().values())
        for playlist in sorted(playlists, Playlist.compare):
            self.playlists.add_playlist(playlist)
            
        self.playlists.get_selection().select_path(0)
        self.playlists.load_playlist(self.playlists)
        
        self.queue_size = 0
        
        gtk.timeout_add(100, self.frame)
        
        gtk.main()
        
    def frame(self):
        'Update widget state based on pending workload.'
        sensitive = async.queue.empty()
        
        self.controls.search_button.set_sensitive(sensitive)
        self.playlists.set_sensitive(sensitive)
        self.tracks.set_sensitive(sensitive)
        
        if not async.queue.empty():
            size = async.queue.qsize()
            if size > self.queue_size:
                self.queue_size = size
            frac = 1.0 - size / float(self.queue_size)
        else:
            self.queue_size, frac = 0, 0.0
        
        self.status.set_progress(frac)
        
        return True

    def destroy(self, widget, data=None):
        'Destroy the window and any resources it holds.'
        if async.thread.is_alive():
            async.thread.shutdown = True
            async.thread.join()
        Window.instance = None
        gtk.main_quit()
        