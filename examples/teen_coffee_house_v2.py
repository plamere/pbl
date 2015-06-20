from pbl import *

'''
    alternate tracks between two different playlists, filtering out any
    tracks by Various Artists
'''

if __name__ == '__main__':
    bad_artists = set(['Various Artists'])
    coffeehouse = ArtistFilter(PlaylistSource('Your Favorite Coffeehouse'), bad_artists)
    teen_party = ArtistFilter(PlaylistSource('Teen Party'), bad_artists)
    both = Alternate([coffeehouse, teen_party])
    show_source(both, ntracks=10)
