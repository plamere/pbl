from pbl import *

'''
    highest energy coffee house shuffled with the lowest energy
    teen party tracks
'''

if __name__ == '__main__':
    bad_artists = set(['Various Artists'])

    coffeehouse = ArtistFilter(PlaylistSource('Your Favorite Coffeehouse'), bad_artists)
    coffeehouse = Annotator(coffeehouse, 'echonest')

    teen_party = ArtistFilter(PlaylistSource('Teen Party'), bad_artists)
    teen_party = Annotator(teen_party, 'echonest')

    both = Alternate([Last(Sorter(coffeehouse, 'echonest.energy'), 8),
        First(Sorter(teen_party, 'echonest.energy'), 8)])
    #both = Shuffle(both)
    show_source(both, props=['echonest.energy', 'src'])
