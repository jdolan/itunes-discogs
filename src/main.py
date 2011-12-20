
from discogs import Discogs
from itunes import Library

import argparse

class iTunesDiscogs:
    
    def __init__(self, arguments):
        self.library, self.discogs = Library(arguments.library), Discogs()

        if not arguments.playlist:
            arguments.playlist = 'Library'
            
        for playlist in self.library.playlists.values():
            if playlist.Name == arguments.playlist:
                self.process_playlist(playlist)
        
    def process_track(self, track):
        if track.is_incomplete():
            print 'Processing %s..' % track,
            release = self.discogs.get_release(track.Artist, track.Name)
            if release:
                print 'Found on %s' % release
            else:
                print 'Not found'        
                
    def process_playlist(self, playlist):
        print 'Processing %s' % playlist
        for tid in playlist.Items:
            self.process_track(self.library.tracks[tid])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Enrich your iTunes library with Discogs', version = '1.0'
    )    
    parser.add_argument('-l', action='store', dest='library',
        help='The iTunes Library filename. If omitted, the default location for the current user is tried.',
    )
    parser.add_argument('-p', action='store', dest='playlist',
        help='The playlist within the iTunes Library to process. If omitted, the entire library will be processed.')
        
    iTunesDiscogs(parser.parse_args())
