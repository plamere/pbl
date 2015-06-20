# -*- coding: latin-1 -*-
import pbl
import unittest
import pprint

from pbl import engine
from pbl.standard_plugs import *
from pbl.spotify_plugs import *
from pbl.echonest_plugs import *

uteen_party ='spotify:user:spotify:playlist:3MlpudZs4HT3i0yGPVfmHC'
ucoffee_house ='spotify:user:spotify:playlist:4BKT5olNFqLB1FAa8OtC8k'
silent_running = False

def runner(source, max_tracks = 100, props=[]):
    if not silent_running:
        pipeline = source
    else:
        pipeline = Dumper(source, props)
    return engine.run_source(pipeline, max_tracks)

class TestPBL(unittest.TestCase):

    def test_playlist_source(self):
        ps = PlaylistSource('Your Favorite Coffeehouse')
        assert(runner(ps, 20) == 20)

    def test_combine_two_playlists(self):
        coffee = PlaylistSource('Your Favorite Coffeehouse')
        teen = PlaylistSource('Teen Party')
        both = Alternate([coffee, teen])
        assert(runner(both, 20) == 20)

    def test_combine_several_playlists(self):
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = PlaylistSource('Teen Party', uteen_party)
        both = Alternate([Looper(coffee), Looper(teen)])
        assert(runner(both,20) == 20)

    def test_shuffle_playlist(self):
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        shuffle = Shuffler(coffee)
        assert(runner(shuffle, 20) == 20)

    def test_track_filtering(self):
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = PlaylistSource('Teen Party', uteen_party)
        both = Alternate([Looper(coffee), Looper(teen)])
        teen2 = First(PlaylistSource('Teen Party', uteen_party))
        filter = TrackFilter(both, teen2)
        assert(runner(filter, 20) == 20)

    def test_fancy_filtering(self):
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = PlaylistSource('Teen Party', uteen_party)
        teen2 = First(PlaylistSource('Teen Party', uteen_party))
        filtered_teen = TrackFilter(teen, teen2)
        both = Alternate([Looper(coffee), Looper(filtered_teen)])
        runner(both, 20)
        assert(runner(both, 20) == 20)


    def test_fancy_combo(self):
        # Put the last 10 songs of teen party at the beginning of coffeehouse
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = Last(PlaylistSource('Teen Party', uteen_party))
        both = Concatenate([teen, coffee])
        assert(runner(both, 20) == 20)

    def test_fancy_combo2(self):
        # Put the 10 random songs of teen party at the beginning of coffeehouse
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = Sample(PlaylistSource('Teen Party', uteen_party))
        both = Concatenate([teen, coffee])
        assert(runner(both, 20) == 20)

    def test_reverse_combo(self):
        # The first 10 songs of coffee house in reverse order
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        pipe = Reverse(First(coffee))
        assert(runner(pipe, 10) == 10)

    def test_fancy_alternating(self):
        # sequence of 4 coffee house tracks followed by one of 4 randomly
        # selected teen party songs

        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = Sample(PlaylistSource('Teen Party', uteen_party), 4)
        pipe = Alternate([coffee] * 4 +  [Looper(teen)])
        assert(runner(pipe, 20) == 20)

    def test_album_combo(self):
        # combine after foreer and the civil wars

        af = AlbumSource('after forever', uri='spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
        vw = AlbumSource('The civil wars', uri='spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
        pipe = Alternate([af, vw])
        assert(runner(pipe, 20) == 20)

    def test_album_source_by_name(self):
        # combine after foreer and the civil wars

        af = AlbumSource('after forever', uri='spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
        vw = AlbumSource('The civil wars', uri='spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
        pipe = Alternate([af, vw])
        assert(runner(pipe, 20) == 20)

    def test_album_combo2(self):
        # combine after forever and the civil wars, but lead with Katy Perry

        af = AlbumSource('after forever', uri='spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
        vw = AlbumSource('The civil wars', uri='spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
        kp = TrackSource(['spotify:track:5jrdCoLpJSvHHorevXBATy'])
        af_vw = Alternate([af, vw])
        pipe = Concatenate([kp, af_vw])
        assert(runner(pipe, 20) == 20)

    def test_album_combo3(self):
        # combine after forever and the civil wars, but lead with Katy Perry

        weezer = ArtistTopTracks('weezer', 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu')
        af = ArtistTopTracks('After Frver','spotify:artist:6ISyfZw4EVt16zhmH2lvxp')
        pipe = Shuffler(Concatenate([weezer, af]))
        assert(runner(pipe, 20) == 20)

    def test_echo_nest_artist_radio(self):
        params = { 
            'type': 'artist-radio',
            'artist': 'weezer',
            'results': 100
        }
        enr = EchoNestPlaylist('weezer radio', params)
        assert(runner(enr, 20) == 20)


    def test_echo_nest_artist_radio_combo(self):
        # mix coffee and weezer radio
        params = { 
            'type': 'artist-radio',
            'artist': 'weezer',
            'results': 50
        }
        weezer = EchoNestPlaylist('weezer radio', params)
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        pipe = Alternate([coffee, weezer])
        assert(runner(pipe, 20) == 20)

    def test_playlist_splitter(self):
        # put first 10 songs of coffeehouse last
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        first, last = Split(coffee, 10).outputs()
        pipe = Concatenate([last, first])
        assert(runner(pipe, 20) == 20)

    def test_playlist_fancy_split_combo(self):
        # play your fav coffeehouse but with 10 of the top 20 songs 
        # from teen party randomly mixed into the first 20 songs

        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        teen = PlaylistSource('Teen Party', uteen_party)

        steen = Sample(First(teen, 20), 10)
        first, last = Split(coffee, 10).outputs() 
        nfirst = Shuffler(Concatenate([steen, first]))
        pipe = Concatenate([nfirst, last])
        assert(runner(pipe, 20) == 20)

    def test_genre_radio(self):
        # create 10 song metal radio and then 10 song jazz radio
        metal = EchoNestGenreRadio('metal', 10)
        jazz = EchoNestGenreRadio('jazz', 10)
        pipe = Concatenate([metal, jazz])
        assert(runner(pipe, 20) == 20)

    def test_genre_radio2(self):
        # create 10 song metal radio and then 10 song jazz radio and then 10 song
        # weezer radio and then 10 songs of after forever
        metal = EchoNestGenreRadio('metal', 10)
        jazz = EchoNestGenreRadio('jazz', 10)
        weezer = EchoNestArtistRadio('weezer', 10)
        af = EchoNestArtistPlaylist('after forever', 10)
        pipe = Concatenate([metal, jazz, weezer, af])
        assert(runner(pipe, 40) == 40)

    def test_genre_radio3(self):
        # create 10 song metal radio and then 10 song jazz radio and then 10 song
        # weezer radio and then 10 songs of after forever
        metal = EchoNestGenreRadio('metal', 10)
        jazz = EchoNestGenreRadio('jazz', 10)
        weezer = EchoNestArtistRadio('weezer', 10)
        af = EchoNestArtistPlaylist('after forever', 10)
        pipe = Alternate([metal, jazz, weezer, af])
        assert(runner(pipe, 40) == 40)

    def test_debugger(self):
        metal = EchoNestGenreRadio('metal', 2)
        dmetal = Debugger(metal)
        assert(runner(dmetal, 2) == 2)

    def test_en_attribute_filter(self):
        ''' find coffeehouse tracks with energy less than .5
        '''
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        he = AttributeRangeFilter(coffee, 'echonest.energy', max_val=.5)
        assert(runner(he, 3) == 3)

    def test_sp_attribute_filter(self):
        ''' find coffeehouse tracks with duration less than 5 mins
        '''
        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        he = AttributeRangeFilter(coffee, 'spotify.duration_ms', max_val=1000 * 60 * 5)
        assert(runner(he, 3) == 3)

    def test_fake_track_tester(self):
        ''' fake track tester
        '''
        coffee = FakeTrackSource()
        assert(runner(coffee, 10) == 10)

    def test_sp_filter_on_en_tracks(self):
        ''' generate echo nest tracks, annotate with spotify data and filter
        '''
        metal = Annotator(EchoNestGenreRadio('metal', 40), 'spotify')
        shortmetal = AttributeRangeFilter(metal, 'spotify.duration_ms', max_val=1000 * 60 * 6)
        assert(runner(shortmetal, 5) == 5)

    def test_en_filter_on_sp_tracks(self):
        ''' generate spotify tracks, annotate with echo nest data and filter
        '''

        coffee = PlaylistSource('coffeehouse', ucoffee_house)
        encoffee = Annotator(coffee, 'echonest')
        high_energy_coffee = AttributeRangeFilter(encoffee, 'echonest.energy', min_val=.5)
        assert(runner(high_energy_coffee, 2) == 2)

    def test_new_style_annotation(self):
        ''' generate echo nest tracks, annotate with spotify data and filter. Using
            new style annoation
        '''

        metal = Annotator(EchoNestGenreRadio('metal', 40), 'spotify')
        shortmetal = AttributeRangeFilter(metal, 'spotify.duration_ms', max_val=1000 * 60 * 5)
        assert(runner(shortmetal, 2) == 2)

    def test_on_the_fly_annotation(self):
        ''' generate echo nest tracks, filter with on-the-fly annotation new-style
        annotation. 
        '''
        metal = EchoNestGenreRadio('metal', 40)
        shortmetal = AttributeRangeFilter(metal, 'spotify.duration_ms', max_val=1000 * 60 * 6)
        assert(runner(shortmetal, 2) == 2)

    def test_date_filter(self):
        ''' find metal from the 1990s
        '''
        metal = EchoNestGenreRadio('metal', 40)
        ninties_metal = AttributeRangeFilter(metal, 'echonest.album_date',
            min_val='1990', max_val='2000')
        assert(runner(ninties_metal, 5) >= 0)

    def test_playlist_save(self):
        ''' save a metal playlist
        '''
        metal = EchoNestGenreRadio('metal', 40)
        pipe = PlaylistSave(metal, 'metal radio2', 'plamere', create=True)
        assert(runner(pipe, 5) == 5)

    def test_playlist_save2(self):
        ''' save a metal playlist
        '''
        metal = EchoNestGenreRadio('metal', 40)
        pipe = PlaylistSave(metal, 'metal radio3', 'plamere', create=False, append=True)
        assert(runner(pipe, 5) == 5)

    def test_save_to_json(self):
        ''' save a metal playlist
        '''
        metal = EchoNestGenreRadio('metal', 40)
        pipe = SaveToJson(metal, 'metal.json')
        assert(runner(pipe, 5) == 5)

    def test_playlist_by_name(self):
        which = 0
        ps = PlaylistSource('Your Favorite Coffeehouse')
        assert(runner(ps, 5) == 5)

    def test_playlist_by_name2(self):
        ''' search for a lesser know playlist
        '''
        ps = PlaylistSource('extender test')
        assert(runner(ps, 5) >= 0)

    def test_playlist_by_name3(self):
        ''' search for a lesser know playlist
        '''
        which = 0
        ps = PlaylistSource('The Pitchfork 500', user='plamere')
        assert(runner(ps, 5) == 5)

    def test_conditional(self):
        ''' If it is sunday, draw from a coffeehouse playlist, else
            draw from teen party
        '''
        ch = PlaylistSource('Your Favorite Coffeehouse')
        tp = PlaylistSource('Teen Party')
        ps = Conditional(is_day_of_week(5), ch, tp)
        assert(runner(ps, 5) == 5)

    def test_case(self):
        source_map = {
            'morning': PlaylistSource('Breakfast In Bed'),
            'afternoon': PlaylistSource('Deep Focus'),
            'evening': PlaylistSource('Teen Party'),
            'night': PlaylistSource('Sleep'),
            'default': PlaylistSource('Music for a Workday')
        }
        ps = Case(get_simple_day_part, source_map)
        assert(runner(ps, 20) == 20)

    def test_album_by_name_and_artist(self):
        ps = AlbumSource('Tarkus', 'Emerson, Lake & Palmer')
        assert(runner(ps, 10) == 7)

    def test_album_by_name(self):
        ps = AlbumSource('Tarkus')
        assert(runner(ps, 10) == 7)

if __name__ == '__main__':
    unittest.main()
