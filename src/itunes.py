
from os.path import expanduser
from plistlib import readPlist

import subprocess

class Track:

    def __init__(self, track):
        self.TrackID = track['Track ID']
        self.PersistentID = track['Persistent ID']
        
        self.Artist = 'Unknown'
        if 'Artist' in track:
            self.Artist = track['Artist']
            
        self.Name = 'Untitled'
        if 'Name' in track:
            self.Name = track['Name']
            
        self.Genre = None
        if 'Genre' in track:
            self.Genre = track['Genre']
            
        self.Year = None
        if 'Year' in track:
            self.Year = track['Year']
            
        self.release = None
            
    def __str__(self):
        return 'Track %s: %s - %s' % (self.TrackID, self.Artist, self.Name)

class Playlist:

    def __init__(self, playlist):
        self.PlaylistID = playlist['Playlist ID']
        self.PlaylistPersistentID = playlist['Playlist Persistent ID']
        
        self.Name = 'Unnamed'
        if 'Name' in playlist:
            self.Name = playlist['Name']
        
        self.Items = []
        if 'Playlist Items' in playlist:
            for i in playlist['Playlist Items']:
                self.Items.append(i['Track ID'])

    def __str__(self):
        return 'Playlist %s: %s' % (self.PlaylistID, self.Name)
    
class Library:

    def __init__(self, library=None):
        if not library:
            library = expanduser('~/Music/iTunes/iTunes Music Library.xml')
        
        plist = readPlist(library)
        
        self.tracks = {}
        for t in plist['Tracks'].values():
            track = Track(t)
            self.tracks[track.TrackID] = track
             
        self.playlists = {}       
        for p in plist['Playlists']:
            playlist = Playlist(p)
            self.playlists[playlist.PlaylistID] = playlist
            
class iTunes:
    
    def __init__(self, library=None):
        self.library = Library(library)
        
        self.bridge = subprocess.Popen(['osascript', '-'], shell=False, stdin=subprocess.PIPE)
        
    def tell(self, cmd):
        self.bridge.communicate(
            """
            tell application "itunes"
                %s
            end tell
            """
        )
        
    def __del__(self):
        self.bridge.terminate()
