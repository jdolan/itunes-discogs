from difflib import SequenceMatcher
import discogs_client as discogs
    
class Matcher(SequenceMatcher):
    
    def __init__(self, s1, s2):
        SequenceMatcher.__init__(self, None, s1, s2)

class Release:
    
    def __init__(self, release):
        self.release = release
        
    def __getattribute__(self, name):
        return self.release.name
    
    def __str__(self):
        return '%s: %s (%s)' % (self.release._id, self.release.title, self.release.data['year'])
                     
class Discogs:
    
    def __init__(self):
        discogs.user_agent = 'iTunes-Discogs/1.0 +http://jdolan.dyndns.org'
        
    def get_release_by_artist(self, artist, title):
        'Attempts to resolve the specified track by exact artist lookup.'
        try:
            releases = discogs.Artist(artist).releases
        except discogs.HTTPError:
            return None
        
        best_ratio, best_release = 0, None
        
        for release in releases:
            for track in release.tracklist:
                ratio = Matcher(title, track['title']).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_release = release
                
        return best_release
    
    def get_release_by_search(self, artist, title):
        'Attempts to resolve the specified track by fuzzy search.'
        query = ('%s %s' % (artist, title)).lower()
        query = ''.join(c for c in query if c.isalnum() or c.isspace())
        
        try:
            results = discogs.Search(query).results()
        except discogs.HTTPError:
            return None
            
        for result in results:
            if isinstance(result, discogs.Release) or isinstance(result, discogs.MasterRelease):
                return result
            return None
        
    def get_release(self, artist, title):
        'Primary entry point for resolving releases for tracks.'
        release = self.get_release_by_search(artist, title)
        
        if not release:
            release = self.get_release_by_artist(artist, title)
           
        if isinstance(release, discogs.Release): 
            if release.master:
                release = release.master
        
        if release:
            return Release(release)
        
        return None
        