from os import mkdir, path
from posixpath import expanduser

NAME = 'iTunes-Discogs'
VERSION = '0.1'    
    
class Field:
    'Field mappings from Discogs to iTunes.'
    
    IGNORE = 'Ignore'
    SET_IF_EMPTY = 'Set if empty'
    OVERWRITE = 'Overwrite'
    
    actions = [IGNORE, SET_IF_EMPTY, OVERWRITE]
    
    def __init__(self, name, source, target, action=IGNORE):
        self.name, self.source, self.target, self.action = name, source, target, action

class Config:
    'The configuration container.'
    def __init__(self, home=None):
        if not home:
            home = expanduser('~/.%s' % NAME)
        self.home = home
        
        if not path.exists(self.home):
            mkdir(self.home)
            
        self.fields = [
            Field('Album', 'album', 'album', Field.SET_IF_EMPTY),
            Field('Artist', 'artist.name', 'artist', Field.IGNORE),
            Field('Label', 'label.name', 'grouping', Field.SET_IF_EMPTY),
            Field('Long Description', 'notes', 'long description', Field.SET_IF_EMPTY),
            Field('Genre', 'genres[0]', 'genre', Field.SET_IF_EMPTY),
            Field('Released', 'released', 'released', Field.SET_IF_EMPTY),
            Field('Title', 'title', 'name', Field.IGNORE),
            Field('Track Number', 'track number', 'track number', Field.SET_IF_EMPTY),
            Field('Year', 'year', 'year', Field.SET_IF_EMPTY)
        ]            
            