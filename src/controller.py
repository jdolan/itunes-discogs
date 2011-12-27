#!/usr/bin/python

from config import Config
from discogs import Discogs
from itunes import iTunes
from model import Model
from view import Window
import argparse
import config
import gobject
import threading
import time

class Controller:
    'The controller implements all application logic.'
    def __init__(self, arguments):
        self.arguments = arguments
        
        self.config = Config(arguments.home)
                
        self.itunes = iTunes(arguments.library)
        
        self.model = Model(self.config, arguments.database, self.get_tracks())
        
        self.discogs = Discogs()
        
        if arguments.cli:
            if not arguments.playlist:
                arguments.playlist = 'Library'
                
            for playlist in self.get_playlists().values():
                if playlist.Name == arguments.playlist:
                    self.process_playlist(playlist)
        else:
            gobject.threads_init()
            Window(self)
            
        self.shutdown()       
    
    def update_track(self, track, fields):
        cmd = 'set t to track 1 of playlist "Library" whose persistent ID is "%s"' % track.PersistentID
        cmd += ''.join(['set %s of t to %s' % (f, v) for (f, v) in fields])
        
        print cmd
        #self.itunes.tell(cmd)
        
    def _get_release(self, track, callback=None, data=None):
        'Performs the grunt work of resolving releases for tracks.'
        release = self.discogs.get_release(track.Artist, track.Name)
        if release:
            self.set_bundle(track.PersistentID, release)
        return release
        
    def _get_release_async(self, track, callback, data):
        'Threaded method for asynchronous release resolution.'
        while threading.active_count() > 5:
            time.sleep(0.1)
            
        release = self._get_release(track)
        gobject.idle_add(callback, track, release, data)
            
    def get_release(self, track, callback=None, data=None):
        'Common entry point for resolving releases for tracks.'
        if callback:
            args = (track, callback, data)
            threading.Thread(target=self._get_release_async, args=args).start()
        else:
            return self._get_release(track)
            
    def process_playlist(self, playlist):
        for tid in playlist.Items:
            track = self.get_track(tid)
            if not track.release:
                track.release = self.get_release(track)
           
    def shutdown(self):
        self.model.flush(self.arguments.database)
        
    def get_tracks(self):
        return self.itunes.library.tracks
    
    def get_track(self, tid):
        return self.get_tracks()[tid]
    
    def get_playlists(self):
        return self.itunes.library.playlists
        
    def get_playlist(self, pid):
        return self.get_playlists()[pid]
    
    def get_bundles(self):
        return self.model.bundles
    
    def get_bundle(self, bid):
        return self.get_bundles()[bid]
    
    def set_bundle(self, bid, data):
        self.model.bundles[bid] = data
        
    def del_bundle(self, bid):
        del self.model.bundles[bid]
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Enrich your iTunes library with Discogs', version = config.VERSION
    )
    parser.add_argument('-c', action='store', dest='cli',
        help='Run this program at the command line. Do not start the GUI.'
    )
    parser.add_argument('-d', action='store', dest='database',
        help='The database file to read and write release associations to.'
    )
    parser.add_argument('-g', action='store', dest='home',
        help='The home directory to store configuration and databases.'
    )
    parser.add_argument('-l', action='store', dest='library',
        help='The iTunes Library filename. If omitted, the default location for the current user is tried.',
    )
    parser.add_argument('-p', action='store', dest='playlist',
        help='The playlist within the iTunes Library to process. If omitted, the entire library will be processed.')
    
    Controller(parser.parse_args())
