import discogs_client as discogs
    
class Release:
    'A proxy class for discogs_client.Release providing easy serialization.'
    def __init__(self, release):
        self.release = release
        self.release.data

    @property
    def uri(self):
        return self._uri.replace('api.', 'www.')
    
    @property
    def year(self):
        return self.data['year']
        
    def __getattr__(self, name):
        return getattr(self.release, name)
    
    def __getstate__(self):
        return {
            'id': self.release._id,
            'content': self._cached_response.content
        }

    def __setstate__(self, state):
        class Response:
            def __init__(self, content):
                self.status_code, self.content = 200, content
                    
        self.release = discogs.Release(state['id'])     
        self.release._cached_response = Response(state['content'])
    
    def __str__(self):
        return '%s: %s (%s)' % (self._id, self.title, self.year)
                     
class Discogs:
    'Provides release lookup based on artist and title.'
    def __init__(self):
        discogs.user_agent = 'iTunes-Discogs/1.0 +http://jdolan.dyndns.org'
        self.junk = ['a', 'feat', 'featuring', 'ft', 'original', 'pres', 'presents', 'mix', 'remix']
                
    def get_release(self, artist, title):
        'Attempts to resolve the specified track by fuzzy search.'        
        query = ('%s %s' % (artist, title)).lower().replace('\'s', '')
        query = ''.join(c for c in query if c.isalnum() or c.isspace())
        
        terms = []
        for term in query.split(' '):
            if term and term not in self.junk:
                terms.append(term)
                
        query = ' '.join(terms[:5])
                
        try:
            results = discogs.Search(query).results()
        except discogs.DiscogsAPIError:
            return None
        
        for result in results:
            if isinstance(result, discogs.Release):
                return Release(result)
            
            if isinstance(result, discogs.MasterRelease):
                return Release(result.key_release)
        
        return None