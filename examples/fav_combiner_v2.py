from pbl import *

'''
    combine four favorite chill out playlists save the back to spotify
'''

if __name__ == '__main__':
    playlist_names = ['Your Favorite Coffeehouse', 'Acoustic Summer',
        'Acoustic Covers', 'Rainy Day']
    all = DeDup(Alternate([Sample(PlaylistSource(n), 10) for n in playlist_names]))
    all = PlaylistSave(all, 'best morning music', 'plamere')
    show_source(all, props=['src'], ntracks=1000000)
