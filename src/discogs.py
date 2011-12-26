from difflib import SequenceMatcher
import discogs_client as discogs
    
class Matcher(SequenceMatcher):
    'A sequence matcher for determining best-match for track names.'
    def __init__(self, s1, s2):
        SequenceMatcher.__init__(self, None, s1, s2)

class Release:
    'A proxy class for discogs_client.Release providing easy serialization.'
    def __init__(self, release):
        self.release = release
    
    @property    
    def year(self):
        return self.data['year']
        
    def __getattr__(self, name):
        return getattr(self.release, name)
    
    def __getstate__(self):
        return {
            '_id' : self._id,
            '_cached_response.content' : self._cached_response.content
        }
    
    def __setstate__(self, d):
        class Response:
            def __init__(self, content):
                self.status_code = 200
                self.content = content
        self.release = discogs.Release(d['_id'])
        self.release._cached_response = Response(d['_cached_response.content'])
        
    def __str__(self):
        return '%s: %s (%s)' % (self._id, self.title, self.year)
                     
class Discogs:
    'Provides release lookup based on artist and title.'
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
           
        if release:
            if isinstance(release, discogs.Release) and release.master:
                release = release.master
                    
            return Release(release)
        
        return None
        