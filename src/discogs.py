import discogs_client as discogs

class Serializable(object):
    'A proxy for discogs_client data types providing safe serialization.'
    def __init__(self, delegate):
        self.delegate = delegate
        self.delegate.data
        
    def __getattr__(self, name):
        return getattr(self.delegate, name)
    
    def __getstate__(self):
        return {
            'id': self.delegate._id,
            'class': self.delegate._uri_name,
            'content': self.delegate._cached_response.content
        }
        
    def __setstate__(self, state):
        class Response:
            def __init__(self, content):
                self.status_code, self.content = 200, content
        
        self.delegate = self._delegate_instance(state['class'], state['id'])
        self.delegate._cached_response = Response(state['content'])
        
    @staticmethod
    def _delegate_instance(c, i):
        classes = {
            'master': discogs.MasterRelease,
            'release': discogs.Release,
            'search': discogs.Search
        }
        return classes[c](i)

class Search(Serializable):
    'A proxy class for discogs_client Search.'
    @property
    def raw_results(self):
        return self.data['searchresults']['results']
    
class Release(Serializable):
    'A proxy for discogs_client Release.'
    @property
    def year(self):
        return self.data['year']
    
    def __str__(self):
        artists = ', '.join([a.name for a in self.artists])
        return '%s: %s - %s (%d)' % (self._id, artists, self.title, self.year)
    
class Discogs:
    'Provides release lookup based on artist and title.'
    def __init__(self):
        discogs.user_agent = 'iTunes-Discogs/1.0 +http://jdolan.dyndns.org'
        self.junk = ['a', 'feat', 'featuring', 'ft', 'original', 'pres', 'presents', 'mix', 'remix', 'vs']
                
    def search(self, artist, title):
        'Attempts to resolve the specified track by fuzzy search.'        
        query = ('%s %s' % (artist, title)).lower().replace('\'s', '')
        query = ''.join(c for c in query if c.isalnum() or c.isspace())
        
        terms = []
        for term in query.split(' '):
            if term and term not in self.junk:
                terms.append(term)
                
        query = ' '.join(terms[:5])       
        
        try:
            return Search(discogs.Search(query))
        except discogs.DiscogsAPIError:
            return []
    
    def release(self, result):
        'Resolve the release for the specified search result.'
        if isinstance(result, discogs.Release):
            return Release(result)
        
        if isinstance(result, discogs.MasterRelease):
            return Release(result.key_release)
        
        return None