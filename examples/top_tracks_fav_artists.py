from pbl import *

'''
    Top tracks by favorite artists
'''

if __name__ == '__main__':
    fav_artists = ['nightwish', 'within temptation', 'epica', 'after forever']
    all = Shuffler(Alternate([ArtistTopTracks(a) for a in fav_artists]))
    all = PlaylistSave(all, 'top gothic metal', 'plamere')
    show_source(all)
