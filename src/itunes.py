
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
            
        self.search, self.release = None, None
            
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
    
    @staticmethod
    def compare(p1, p2):
        return cmp(p1.Name, p2.Name)
        
class Library:

    def __init__(self, library=None):
        if not library:
            library = expanduser('~/Music/iTunes/iTunes Music Library.xml')
        
        plist = readPlist(library)
        
        self.tracks = {}
        for t in plist['Tracks'].values():
            
            if t['Track Type'] != 'File':
                continue
            
            track = Track(t)
            
            self.tracks[track.TrackID] = track
            self.tracks[track.PersistentID] = track
             
        self.playlists = {}       
        for p in plist['Playlists']:
            
            if 'Distinguished Kind' in p:
                continue
            
            playlist = Playlist(p)
            
            self.playlists[playlist.PlaylistID] = playlist
            self.playlists[playlist.PlaylistPersistentID] = playlist
            
class iTunes:
    
    def __init__(self, model, library=None):
        self.model, self.library = model, Library(library)            
        self.bridge = subprocess.Popen(['osascript', '-'], shell=False, stdin=subprocess.PIPE)
        
        for track in self.library.tracks.values():
            search = self.model.get_bundle('track.search', track.PersistentID)
            if search:
                track.search = self.model.get_bundle('search', search)
                
            release = self.model.get_bundle('track.release', track.PersistentID)
            if release:
                track.release = self.model.get_bundle('release', release)
    
    def update_track(self, track, fields):
        'Back release information into iTunes.'
        cmd = 'set t to track 1 of playlist "Library" whose persistent ID is "%s"' % track.PersistentID
        cmd += ''.join(['set %s of t to %s' % (f, v) for (f, v) in fields])
        
        print cmd
        #self._tell(cmd)
        
    def _tell(self, cmd):
        self.bridge.communicate(
            """
            tell application "itunes"
                %s
            end tell
            """
        )
        
    def __del__(self):
        self.bridge.terminate()
