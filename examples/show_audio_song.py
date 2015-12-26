from pbl import *

'''
    Dump out a single track to show the available attributes on a 
    Spotify Track
'''

if __name__ == '__main__':
    teen_party = PlaylistSource('Teen Party')
    teen_party = Annotator(teen_party, 'spotify')
    teen_party = Annotator(teen_party, 'audio')
    show_source(Debugger(teen_party), 1)
