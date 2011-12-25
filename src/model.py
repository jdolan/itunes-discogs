from os import path
from posixpath import expanduser
import cPickle

class Bundle:
    
    def __init__(self, bid, data):
        self.bid, self.data = bid, data

class Model:
    'Provides simple key-value pair persistence.'
    def __init__(self, database=None):
        if not database:
            database = expanduser('~/.iTunes-Discogs/db')
               
        self.bundles = {}
        
        if path.exists(database): 
            with open(database, 'r') as db:
                self.bundles = cPickle.load(db)
                        
    def flush(self, database=None):
        print 'flushing'
        if not database:
            database = expanduser('~/.iTunes-Discogs/db')
            
        with open(database, 'w') as db:
            cPickle.dump(self.bundles, db)
            
    