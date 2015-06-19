
from pbl import *

'''
    combine tracks from your favorite coffeen house and teen party
'''

if __name__ == '__main__':
    bad_artists = set(['Various Artists'])
    coffeehouse = ArtistFilter(bad_artists, PlaylistSource('Your Favorite Coffeehouse'))
    teen_party = ArtistFilter(bad_artists, PlaylistSource('Teen Party'))
    both = Alternate([coffeehouse, teen_party])
    shuffle = Shuffler(both)
    show_source(shuffle, ntracks=10)
