import pbl

'''
    alternate tracks between two different playlists
'''

if __name__ == '__main__':
    coffeehouse = pbl.PlaylistSource('Your Favorite Coffeehouse')
    teen_party = pbl.PlaylistSource('Teen Party')
    both = pbl.Alternate([coffeehouse, teen_party])
    pbl.show_source(both, ntracks=10)
