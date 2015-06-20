from pbl import *

'''
    dad and daughter agree that their morning drive playlist, should be split
    50/50 between classic jazz and teen party. Selfish dad creates this playlist
    builder that combines the longest classic jazz songs with the shortest teen
    party songs
'''

if __name__ == '__main__':
    teen_party = First(Sorter(PlaylistSource('Teen Party'), 'spotify.duration_ms'), 10)
    jazz_classics = Last(Sorter(PlaylistSource('Jazz Classics'), 'spotify.duration_ms'), 10)
    both = Alternate([teen_party, Reverse(jazz_classics)])
    show_source(both, props=['spotify.duration_ms', 'src'])
