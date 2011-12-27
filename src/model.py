from os import path
import cPickle
import gzip

class Model:
    'Provides simple key-value pair persistence.'
    def __init__(self, config, database=None, tracks={}):
        self.config = config
        
        if not database:
            database = self.default_database()
               
        self.bundles = {}
        
        if path.exists(database): 
            with gzip.open(database, 'r') as db:
                self.bundles = cPickle.load(db)
        
        for (bid, data) in self.bundles.items():
            if bid in tracks:
                tracks[bid].release = data
                
    def default_database(self):
        return '%s/db' % self.config.home
                        
    def flush(self, database=None):
        if not database:
            database = self.default_database()
            
        with gzip.open(database, 'w') as db:
            cPickle.dump(self.bundles, db)
            