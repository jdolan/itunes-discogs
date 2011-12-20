
from os.path import expanduser
from plistlib import readPlist

class Track:

    def __init__(self, track):
        self.TrackID = track['Track ID']
        
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
            
    def is_incomplete(self):
        if self.Genre != 'Mixed':
            if self.Artist != 'Unknown' and self.Name != 'Untitled':
                return self.Year is None
        return False
            
    def __str__(self):
        return 'Track %s: %s - %s' % (self.TrackID, self.Artist, self.Name)

class Playlist:

    def __init__(self, playlist):
        self.PlaylistID = playlist['Playlist ID']
        
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

    def __init__(self, library=None, playlist=None):
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
