from pbl import *

'''
    sort the songs in a playlist by their title length
'''

if __name__ == '__main__':
    teen_party = Sorter(PlaylistSource('Teen Party'), 'title')
    show_source(teen_party)
