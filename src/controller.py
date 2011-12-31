#!/usr/bin/python

from config import Config
from discogs import Discogs
from itunes import iTunes
from model import Model
from view import Window
import argparse
import config

class Controller:
    'The controller implements all application logic.'         
    def __init__(self, arguments):
        'Main entry point for iTunes-Discogs.'
        self.arguments = arguments
        self.config = Config(arguments.home)
        self.model = Model(self.config, arguments.database)
        self.itunes = iTunes(self.model, arguments.library)
        self.discogs = Discogs(self.model, arguments.junk)
                
        if arguments.cli:
            if not arguments.playlist:
                arguments.playlist = 'Library'
                
            for playlist in self.get_playlists().values():
                if playlist.Name == arguments.playlist:
                    self._process_playlist(playlist)
        else:
            Window(self)
            
        self.shutdown()
        
    def search(self, track):
        'Search storing results in the database.'
        track.search = self.discogs.search(track.Artist, track.Name)
        if track.search:
            self.model.set_bundle('track.search', track.PersistentID, track.search._id)
            if track.search.raw_results and not track.release:
                self.set_release(track, track.search.raw_results[0])
            
    def set_release(self, track, result):
        'Sets the track release to the specified result.'
        track.release = self.discogs.get_release(result)
        if track.release:
            self.model.set_bundle('track.release', track.PersistentID, track.release._id)
             
    def _process_playlist(self, playlist):
        'Resolve releases for the specified playlist.'
        for tid in playlist.Items:
            track = self.get_track(tid)
            if not track.release:
                self.search(track)
                if track.search and track.search.results():
                    self.set_release(track, track.search.results()[0])
                
    def shutdown(self):
        'Shutdown the worker thread and flush the database.'
        self.model.flush(self.arguments.database)
        
    def get_tracks(self):
        return self.itunes.library.tracks
    
    def get_track(self, tid):
        return self.get_tracks()[tid]
    
    def get_playlists(self):
        return self.itunes.library.playlists
        
    def get_playlist(self, pid):
        return self.get_playlists()[pid]
        
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
    parser.add_argument('-j', action='store', default='', dest='junk',
        help='Junk terms to exclude from search queries.'
    )
    parser.add_argument('-l', action='store', dest='library',
        help='The iTunes Library filename. If omitted, the default location for the current user is tried.',
    )
    parser.add_argument('-p', action='store', dest='playlist',
        help='The playlist within the iTunes Library to process. If omitted, the entire library will be processed.')
    
    Controller(parser.parse_args())
