#!/usr/bin/python

from discogs import Discogs
from itunes import iTunes
from model import Model
from os import mkdir, path
from threading import Thread
from view import Window
import argparse
import gobject

class Controller:
    
    def __init__(self, arguments):
        self.arguments = arguments
        
        self.itunes, self.discogs = iTunes(arguments.library), Discogs()
        
        self.home = path.expanduser('~/.iTunes-Discogs')
        
        if not path.exists(self.home):
            mkdir(self.home)
        
        self.model = Model(arguments.database)
        
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
        release = self.discogs.get_release(track.Artist, track.Name)
        if release:
            self.set_bundle(track.PersistentID, release)
        if callback:
            gobject.idle_add(callback, track, release, data)
        else:
            return release
            
    def get_release(self, track, callback=None, data=None):
        if callback:
            Thread(target=self._get_release, args=(track, callback, data)).start()
        else:
            return self._get_release(track)
            
    def process_playlist(self, playlist):
        for tid in playlist.Items:
            track = self.get_track(tid)
            if track.PersistentID not in self.get_bundles():
                self.get_release(self.get_track(tid))
           
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
        description = 'Enrich your iTunes library with Discogs', version = '1.0'
    )
    parser.add_argument('-c', action='store', dest='cli',
        help='Run this program at the command line. Do not start the GUI.'
    )
    parser.add_argument('-d', action='store', dest='database',
        help='The database file to read and write release associations to.'
    )
    parser.add_argument('-l', action='store', dest='library',
        help='The iTunes Library filename. If omitted, the default location for the current user is tried.',
    )
    parser.add_argument('-p', action='store', dest='playlist',
        help='The playlist within the iTunes Library to process. If omitted, the entire library will be processed.')
    
    Controller(parser.parse_args())
