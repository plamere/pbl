from pbl import *

'''
    dad and daughter agree that their morning drive playlist, should be split
    50/50 between classic rock and teen party. Selfish dad creates this playlist
    builder that combines the longest classic rock songs with the shortest teen
    part songs
'''

if __name__ == '__main__':
    teen_party = First(Sorter(PlaylistSource('Teen Party'), 'spotify.duration_ms'), 10)
    classic_rock = Last(Sorter(PlaylistSource('Rock Classics'), 'spotify.duration_ms'), 10)
    both = Alternate([teen_party, Reverse(classic_rock)])
    show_source(both, props=['spotify.duration_ms', 'src'])
