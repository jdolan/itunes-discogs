from os import path
import cPickle
import gzip

class Model:
    'Provides simple key-value pair persistence.'
    def default_database(self):
        return '%s/db' % self.config.home
    
    def __init__(self, config, database=None):
        'Initializes the persistent store.'
        self.config = config
        
        if not database:
            database = self.default_database()
            
        self.bundles = {}
        
        if path.exists(database): 
            with gzip.open(database, 'r') as db:
                self.bundles = cPickle.load(db)
        
    def get_bundles(self, _type):
        'Returns the dictionary of bundles by the specified type.'
        if _type not in self.bundles:
            self.bundles[_type] = {}
        return self.bundles[_type]
    
    def get_bundle(self, _type, _id):
        'Returns the bundle by the specified type and id, or None.'
        if _id in self.get_bundles(_type):
            return self.get_bundles(_type)[_id]
        return None
    
    def set_bundle(self, _type, _id, data):
        'Sets the bundle with the specified type and id.'
        self.get_bundles(_type)[_id] = data
        
    def del_bundle(self, _type, _id):
        'Deletes the bundle by the specified type and id.'
        if _id in self.get_bundles(_type):
            del self.get_bundles(_type)[_id]
                        
    def flush(self, database=None):
        'Flushes all bundles to the filesystem.'
        if not database:
            database = self.default_database()
            
        with gzip.open(database, 'w') as db:
            cPickle.dump(self.bundles, db)
            