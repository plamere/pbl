from pbl import *

'''
    alternate tracks between two different playlists, filtering out any
    tracks by Various Artists
'''

if __name__ == '__main__':
    bad_artists = set(['Various Artists'])
    coffeehouse = ArtistFilter(bad_artists, PlaylistSource('Your Favorite Coffeehouse'))
    teen_party = ArtistFilter(bad_artists, PlaylistSource('Teen Party'))
    both = Alternate([coffeehouse, teen_party])
    show_source(both, ntracks=10)
