import discogs_client as discogs

discogs.user_agent = 'iTunes-Discogs/1.0 +http://jdolan.dyndns.org'

class Serializable(object):
    'A proxy for discogs_client data types providing safe serialization.'
    def __init__(self, delegate):
        self.delegate = delegate
        self.delegate.data
        
    def __getattr__(self, name):
        return getattr(self.delegate, name)
    
    def __getstate__(self):
        return {
            '_type': self.delegate._uri_name,
            '_id': self.delegate._id,
            'content': self.delegate._cached_response.content
        }
        
    def __setstate__(self, state):
        self.delegate = self._delegate_instance(
            state['_type'], state['_id'], state['content']
        )
        
    @staticmethod
    def _delegate_instance(_type, _id, content=None):
        'Return the delegate instance for the specified parameters.'
        class Response:
            def __init__(self, content):
                self.status_code, self.content = 200, content
                
        classes = {
            'master': discogs.MasterRelease,
            'release': discogs.Release,
            'search': discogs.Search
        }
        
        delegate = classes[_type](_id)
        if content:
            delegate._cached_response = Response(content)
        
        return delegate

class Search(Serializable):
    'A proxy class for discogs_client Search.'
    class RawResult:
        'A proxy for search results, allowing lazy-loading of key attributes.'
        def __init__(self, data):
            self.data = data
            
        @property
        def _type(self):
            return self.data['type']
           
        @property
        def _id(self):
            return self.data['uri'].split('/')[-1]
        
        @property
        def title(self):
            return self.data['title']
        
        def to_object(self):
            return Serializable._delegate_instance(self._type, self._id)
         
        def __str__(self):
            return '%s: %s' % (self._id, self.title)
    
    @property
    def raw_results(self): 
        return [Search.RawResult(r) for r in self.data['searchresults']['results']]
        
class Release(Serializable):
    'A proxy for discogs_client Release.'
    @property
    def year(self):
        return self.data['year']
    
    def __str__(self):
        artists = ', '.join([a['name'] for a in self.data.get('artists', [])])
        return '%s: %s - %s (%d)' % (self._id, artists, self.title, self.year)
    
class Discogs:
    'A facade for discogs_client exposing convenient search and release lookup.'
    def __init__(self, model, junk=''):
        self.model = model
        
        self.junk = [
            'a', 'feat', 'featuring', 'ft',
            'original', 'pres', 'presents', 
            'mix', 'mp3', 'remix', 'vs'
        ] + junk.split(' ')
    
    def _get_query(self, artist, title):
        query = ('%s %s' % (artist, title)).lower().replace('\'s', '')
        query = ''.join(c for c in query if c.isalnum() or c.isspace())
        
        terms = []
        for term in query.split(' '):
            if term and term not in self.junk:
                terms.append(term)
                
        return ' '.join(terms[:5])
        
    def search(self, artist, title):
        'Search for releases for the specified artist and title.'
        query = self._get_query(artist, title)
        search = self.model.get_bundle('search', query)
        if not search:
            try:
                search = Search(discogs.Search(query))
            except discogs.DiscogsAPIError:
                pass
            self.model.set_bundle('search', query, search)
        return search
           
    def get_release(self, result):
        'Fetch the release object for the specified search result.'
        release = self.model.get_bundle('release', result._id)
        if not release:
            if isinstance(result, Search.RawResult):
                result = result.to_object()
                
            if isinstance(result, discogs.Release):
                release = Release(result)
            
            if isinstance(result, discogs.MasterRelease):
                release = Release(result.key_release)
                                            
            for _id in set([result._id, release._id]):
                self.model.set_bundle('release', _id, release)
        return release