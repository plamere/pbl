import sys
import engine
from standard_plugs import *
from spotify_plugs import *
from echonest_plugs import *
#from track_manager import tlib
from frog import *

uteen_party ='spotify:user:spotify:playlist:3MlpudZs4HT3i0yGPVfmHC'
ucoffee_house ='spotify:user:spotify:playlist:4BKT5olNFqLB1FAa8OtC8k'

def runner(source, max_tracks = 100, props=[]):
    pipeline = Dumper(source, props)
    print
    print 'running', source.name
    engine.run_source(pipeline, max_tracks)
    print

def tester1():
    which = 0
    ps = PlaylistSource('coffeehouse', ucoffee_house)
    runner(ps)

def tester2():
    # combine several playlists
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = PlaylistSource('Teen Party', uteen_party)
    both = Alternate([coffee, teen])
    runner(both)

def tester3():
    # combine several playlists
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = PlaylistSource('Teen Party', uteen_party)
    both = Alternate([Looper(coffee), Looper(teen)])
    runner(both)

def tester4():
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    shuffle = Shuffler(coffee)
    runner(shuffle)

def tester5():
    # combine several playlists
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = PlaylistSource('Teen Party', uteen_party)
    both = Alternate([Looper(coffee), Looper(teen)])
    teen2 = First(PlaylistSource('Teen Party', uteen_party))
    filter = TrackFilter(both, teen2)
    runner(filter, 20)

def tester6():
    # combine several playlists
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = PlaylistSource('Teen Party', uteen_party)
    teen2 = First(PlaylistSource('Teen Party', uteen_party))
    filtered_teen = TrackFilter(teen, teen2)
    both = Alternate([Looper(coffee), Looper(filtered_teen)])
    runner(both, 20)

def tester7():
    # Put the last 10 songs of teen party at the beginning of coffeehouse
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = Last(PlaylistSource('Teen Party', uteen_party))
    both = Concatenate([teen, coffee])
    runner(both)

def tester8():
    # Put the 10 random songs of teen party at the beginning of coffeehouse
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = Sample(PlaylistSource('Teen Party', uteen_party))
    both = Concatenate([teen, coffee])
    runner(both)

def tester9():
    # The first 10 songs of coffee house in reverse order
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    pipe = Reverse(First(coffee))
    runner(pipe)

def tester10():
    # sequence of 4 coffee house tracks followed by one of 4 randomly
    # selected teen party songs

    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = Sample(PlaylistSource('Teen Party', uteen_party), 4)
    pipe = Alternate([coffee] * 4 +  [Looper(teen)])
    runner(pipe)

def tester11():
    # combine after foreer and the civil wars

    af = AlbumSource('after forever', 'spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
    vw = AlbumSource('The civil wars', 'spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
    pipe = Alternate([af, vw])
    runner(pipe)

def tester12():
    # combine after forever and the civil wars, but lead with Katy Perry

    af = AlbumSource('after forever', 'spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
    vw = AlbumSource('The civil wars', 'spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
    kp = TrackSource(['spotify:track:5jrdCoLpJSvHHorevXBATy'])
    af_vw = Alternate([af, vw])
    pipe = Concatenate([kp, af_vw])
    runner(pipe)

def tester13():
    # combine after forever and the civil wars, but lead with Katy Perry

    weezer = ArtistTopTracks('weezer', 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu')
    af = ArtistTopTracks('After Frver','spotify:artist:6ISyfZw4EVt16zhmH2lvxp')
    pipe = Shuffler(Concatenate([weezer, af]))
    runner(pipe)

def tester14():
    params = { 
        'type': 'artist-radio',
        'artist': 'weezer',
        'results': 100
    }
    enr = EchoNestPlaylist('weezer radio', params)
    runner(enr)


def tester15():
    # mix coffee and weezer radio
    params = { 
        'type': 'artist-radio',
        'artist': 'weezer',
        'results': 50
    }
    weezer = EchoNestPlaylist('weezer radio', params)
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    pipe = Alternate([coffee, weezer])
    runner(pipe)

def tester16():
    # put first 10 songs of coffeehouse last
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    first, last = Split(coffee, 10).outputs()
    pipe = Concatenate([last, first])
    runner(pipe)

def tester17():
    # play your fav coffeehouse but with 10 of the top 20 songs 
    # from teen party randomly mixed into the first 20 songs

    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = PlaylistSource('Teen Party', uteen_party)

    steen = Sample(First(teen, 20), 10)
    first, last = Split(coffee, 10).outputs() 
    nfirst = Shuffler(Concatenate([steen, first]))
    pipe = Concatenate([nfirst, last])
    runner(pipe)

def tester18():
    # create 10 song metal radio and then 10 song jazz radio
    metal = EchoNestGenreRadio('metal', 10)
    jazz = EchoNestGenreRadio('jazz', 10)
    pipe = Concatenate([metal, jazz])
    runner(pipe)

def tester19():
    # create 10 song metal radio and then 10 song jazz radio and then 10 song
    # weezer radio and then 10 songs of after forever
    metal = EchoNestGenreRadio('metal', 10)
    jazz = EchoNestGenreRadio('jazz', 10)
    weezer = EchoNestArtistRadio('weezer', 10)
    af = EchoNestArtistPlaylist('after forever', 10)
    pipe = Concatenate([metal, jazz, weezer, af])
    runner(pipe)

def tester20():
    # create 10 song metal radio and then 10 song jazz radio and then 10 song
    # weezer radio and then 10 songs of after forever
    metal = EchoNestGenreRadio('metal', 10)
    jazz = EchoNestGenreRadio('jazz', 10)
    weezer = EchoNestArtistRadio('weezer', 10)
    af = EchoNestArtistPlaylist('after forever', 10)
    pipe = Alternate([metal, jazz, weezer, af])
    runner(pipe)

def tester21():
    metal = EchoNestGenreRadio('metal', 2)
    runner(Debugger(metal))

def tester22():
    ''' find coffeehouse tracks with energy greater than .5
    '''
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    he = AttributeRangeFilter(coffee, 'echonest.energy', min_val=.5)
    runner(Debugger(he))

def tester23():
    ''' find coffeehouse tracks with duration less than 3 mins
    '''
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    he = AttributeRangeFilter(coffee, 'spotify.duration_ms', max_val=1000 * 60 * 3)
    runner(he,props=['spotify.duration_ms'])

def tester24():
    ''' fake track tester
    '''
    coffee = FakeTrackSource()
    runner(coffee)

def tester25():
    ''' generate echo nest tracks, annotate with spotify data and filter
    '''
    metal = Annotator(EchoNestGenreRadio('metal', 40), 'spotify')
    shortmetal = AttributeRangeFilter(metal, 'spotify.duration_ms', max_val=1000 * 60 * 3)
    runner(shortmetal)

def tester26():
    ''' generate spotify tracks, annotate with echo nest data and filter
    '''

    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    encoffee = Annotator(coffee, 'echonest')
    high_energy_coffee = AttributeRangeFilter(encoffee, 'echonest.energy', min_val=.5)
    runner(high_energy_coffee, props=['spotify.duration_ms', 'echonest.energy'])

def tester27():
    ''' generate echo nest tracks, annotate with spotify data and filter. Using
        new style annoation
    '''

    metal = Annotator(EchoNestGenreRadio('metal', 40), 'spotify')
    shortmetal = AttributeRangeFilter(metal, 'spotify.duration_ms', max_val=1000 * 60 * 3)
    runner(Debugger(shortmetal))

def tester28():
    ''' generate echo nest tracks, filter with on-the-fly annotation new-style
    annotation. 
    '''

    metal = EchoNestGenreRadio('metal', 40)
    shortmetal = AttributeRangeFilter(metal, 'spotify.duration_ms', max_val=1000 * 60 * 3)
    runner(shortmetal)

def tester29():
    ''' find metal from the 1990s
    '''
    metal = EchoNestGenreRadio('metal', 40)
    ninties_metal = AttributeRangeFilter(metal, 'echonest.album_date',
        min_val='1990', max_val='2000')
    runner(ninties_metal, props=['echonest.album_date'])

def tester30():
    ''' save a metal playlist
    '''
    metal = EchoNestGenreRadio('metal', 40)
    pipe = PlaylistSave(metal, 'metal radio2', 'plamere', create=True)
    runner(pipe)

def tester31():
    ''' save a metal playlist
    '''
    metal = EchoNestGenreRadio('metal', 40)
    pipe = PlaylistSave(metal, 'metal radio3', 'plamere', create=False, append=True)
    runner(pipe)

def tester32():
    ''' save a metal playlist
    '''
    metal = EchoNestGenreRadio('metal', 40)
    pipe = SaveToJson(metal, 'metal.json')
    runner(pipe)

def tester33():
    which = 0
    ps = PlaylistSource('Your Favorite Coffeehouse')
    runner(ps)

def tester34():
    ''' search for a lesser know playlist
    '''
    which = 0
    ps = PlaylistSource('extender test')
    runner(ps)

def tester35():
    ''' search for a lesser know playlist
    '''
    which = 0
    ps = PlaylistSource('The Pitchfork 500', user='plamere')
    runner(ps, max_tracks=500)

def tester36():
    ''' If it is sunday, draw from a coffeehouse playlist, else
        draw from teen party
    '''
    ch = PlaylistSource('Your Favorite Coffeehouse')
    tp = PlaylistSource('Teen Party')
    ps = Conditional(is_day_of_week(5), ch, tp)
    runner(ps)

def tester37():
    source_map = {
        'morning': PlaylistSource('Breakfast In Bed'),
        'afternoon': PlaylistSource('Deep Focus'),
        'evening': PlaylistSource('Teen Party'),
        'night': PlaylistSource('Sleep'),
        'default': PlaylistSource('Music for a Workday')
    }
    ps = Case(get_simple_day_part, source_map)
    runner(ps)

def tester38():
    ''' boil the frog
    '''
    which = 0
    ps = BoilTheFrogSource('Elvis Presley', 'Weezer')
    runner(ps, max_tracks=500)

def tester39():
    ''' album by name
    '''
    which = 0
    ps = AlbumSource('Tarkus', 'Emerson, Lake & Palmer')
    runner(ps, max_tracks=20)

def tester40():
    ''' album by name
    '''
    which = 0
    ps = AlbumSource('Tarkus')
    runner(ps, max_tracks=20)

def tester41():
    ''' No more than 30 mins of tarkus
    '''
    ps = ShorterThan(AlbumSource('Tarkus'), 30 * 60)
    runner(ps)

def tester42():
    ''' No less than 30 mins of tarkus
    '''
    ps = LongerThan(AlbumSource('Tarkus'), 30 * 60)
    runner(ps)

def tester43():
    ''' Sort by title length
    '''
    ps = CustomSorter(PlaylistSource('Teen Party'), lambda tid: len(tlib.get_attr(tid, 'title')))
    runner(ps)


if __name__ == '__main__':
    tester43()
    
