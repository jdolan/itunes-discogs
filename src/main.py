#!/usr/bin/python

from discogs import Discogs
from itunes import iTunes
from ui import Window

import argparse

class Controller:
    
    def __init__(self, arguments):
        self.itunes, self.discogs = iTunes(arguments.library), Discogs()
        
        if arguments.cli:
            if not arguments.playlist:
                arguments.playlist = 'Library'
                
            for playlist in self.get_playlists().values():
                if playlist.Name == arguments.playlist:
                    self.process_playlist(playlist)
        
        else:
            Window(self)
            
    def get_tracks(self):
        return self.itunes.library.tracks
    
    def get_track(self, tid):
        return self.get_tracks()[tid]
    
    def get_playlists(self):
        return self.itunes.library.playlists
        
    def get_playlist(self, pid):
        return self.get_playlists()[pid]
    
    def get_releases(self):
        return self.discogs.releases
    
    def get_release(self, rid):
        return self.get_releases()[rid]
    
    def update_track(self, track, fields):
        cmd = 'set t to track 1 of playlist "Library" whose persistent ID is "%s"' % track.PersistentID
        cmd += ''.join(['set %s of t to %s' % (f, v) for (f, v) in fields])
        
        print cmd
        #self.itunes.tell(cmd)
        
    def process_track(self, track, callback=None, data=None):
        print 'Processing %s..' % track,
        release = self.discogs.get_release(track.Artist, track.Name)
        if release:
            print 'Found on %s' % release
            if callback:
                callback(track, release, data) 
        else:
            print 'Not found'
                
    def process_playlist(self, playlist):
        print 'Processing %s..' % playlist
        for tid in playlist.Items:
            self.process_track(self.get_track(tid))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Enrich your iTunes library with Discogs', version = '1.0'
    )
    parser.add_argument('-c', action='store', dest='cli',
        help='Run this program at the command line. Do not start the GUI.'
    )
    parser.add_argument('-l', action='store', dest='library',
        help='The iTunes Library filename. If omitted, the default location for the current user is tried.',
    )
    parser.add_argument('-p', action='store', dest='playlist',
        help='The playlist within the iTunes Library to process. If omitted, the entire library will be processed.')
    
    Controller(parser.parse_args())
