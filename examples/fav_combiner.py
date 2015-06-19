from pbl import *

'''
    combine four favorite chill out playlists  into a new list
'''

if __name__ == '__main__':
    playlist_names = ['Your Favorite Coffeehouse', 'Acoustic Summer',
        'Acoustic Covers', 'Rainy Day']
    all = DeDup(Alternate([Sample(PlaylistSource(n), 10) for n in playlist_names]))
    show_source(all, props=['src'])
