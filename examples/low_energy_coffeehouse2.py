import pbl

'''
    30 minutes of the lowest energy tracks from your 
    favorite coffeehouse
'''

if __name__ == '__main__':
    coffeehouse = pbl.PlaylistSource('Your Favorite Coffeehouse')
    coffeehouse = pbl.Annotator(coffeehouse, 'audio')
    coffeehouse = pbl.Sorter(coffeehouse, 'audio.energy')
    coffeehouse = pbl.LongerThan(coffeehouse, 30 * 60)
    pbl.show_source(coffeehouse, props=['duration', 'spotify', 'audio.energy'])
