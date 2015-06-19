from pbl import *

'''
    highest energy coffee house shuffled with the lowest energy
    teen party tracks
'''

if __name__ == '__main__':
    bad_artists = set(['Various Artists'])

    coffeehouse = ArtistFilter(bad_artists, PlaylistSource('Your Favorite Coffeehouse'))
    coffeehouse = Annotator(coffeehouse, 'echonest')

    teen_party = ArtistFilter(bad_artists, PlaylistSource('Teen Party'))
    teen_party = Annotator(teen_party, 'echonest')

    both = Alternate([Last(Sorter(coffeehouse, 'echonest.energy'), 8),
        First(Sorter(teen_party, 'echonest.energy'), 8)])
    #both = Shuffle(both)
    show_source(both, props=['echonest.energy', 'src'])
