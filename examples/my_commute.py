from pbl import *

'''
    combine some classic rock and New Music Tuesday
'''

classic_rock = Sample(PlaylistSource('Rock Classics'), sample_size=10)
new_music = Sample(PlaylistSource('New Music Tuesday'), sample_size=5)
combined = Shuffler(Concatenate([classic_rock, new_music]))
show_source(combined)
