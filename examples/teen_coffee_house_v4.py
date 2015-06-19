from pbl import *

'''
    combine tracks from your favorite coffeen house and teen party
    sort by increasing energy
'''

if __name__ == '__main__':
    bad_artists = set(['Various Artists'])
    coffeehouse = ArtistFilter(bad_artists, PlaylistSource('Your Favorite Coffeehouse'))
    teen_party = ArtistFilter(bad_artists, PlaylistSource('Teen Party'))
    both = Alternate([coffeehouse, teen_party])
    both = Buffer(both, 16)
    both = Annotator(both, 'echonest')
    sorted = Sorter(both, 'echonest.energy')
    show_source(sorted, props=['echonest.energy', 'src'])
