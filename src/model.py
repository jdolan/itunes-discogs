from os import path
from posixpath import expanduser
import cPickle

class Model:
    'Provides simple key-value pair persistence.'
    def __init__(self, database=None, tracks={}):
        if not database:
            database = expanduser('~/.iTunes-Discogs/db')
               
        self.bundles = {}
        
        if path.exists(database): 
            with open(database, 'r') as db:
                self.bundles = cPickle.load(db)
        
        for (bid, data) in self.bundles.items():
            if bid in tracks:
                tracks[bid].release = data
                        
    def flush(self, database=None):
        if not database:
            database = expanduser('~/.iTunes-Discogs/db')
            
        with open(database, 'w') as db:
            cPickle.dump(self.bundles, db)
            