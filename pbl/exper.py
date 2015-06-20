import spotipy
import random
import pyen
import pprint
import json
from spotipy.oauth2 import SpotifyClientCredentials


client_credentials_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
en = pyen.Pyen()


en_song_buckets = [
    'id:spotify', 'audio_summary', 'song_hotttnesss_rank', 'song_hotttnesss',
    'song_currency_rank', 'song_currency', 'artist_hotttnesss', 
    'artist_familiarity', 'artist_discovery'
]

spotify.trace = False

'''
    general rules:
        all sources must eventually be finite
        only pull your source on a next_track call
        only pull as many tracks as you need

'''

class TrackLibrary:
    
    def __init__(self):
        self.tmap = { }

    def add_track(self, source_name, tid, info):
        info['src'] = source_name
        self.tmap[tid] = info

    def get_track(self, tid):
        return self.tmap[tid]

    def get_tn(self, tid):
        track = self.get_track(tid)
        if track:
            return track['name'] + ' ' + track['artists'][0]['name'] \
                + ' from ' + track['src']
        else:
            return '(none)'


    def get_track_attribute(self, tid, attribute):
        pass
        


    def is_valid_attribute(attr):
        return attr in self.attr_map

    def flatten_en_song(self, song):
        for k,v in song['audio_summary'].items():
            song[k] = v
        del song['artist_foreign_ids']
        del song['audio_summary']
        del song['analysis_url']
        return song


tlib = TrackLibrary()

class PlaylistSource:

    def __init__(self, name, uri):
        self.name = name
        self.uri = uri

        self.next_offset = 0
        self.limit = 100

        self.tracks = []
        self.total = 1
        self.cur_index = 0

    def _get_more_tracks(self):
        _,_,user,_,playlist_id = self.uri.split(':')
        results = spotify.user_playlist_tracks(user, playlist_id, 
            limit=self.limit, offset=self.next_offset)

        self.total = results['total']
        for item in results['items']:
            track = item['track']
            self.tracks.append(track['id'])
            tlib.add_track(self.name, track['id'], track)
        self.next_offset += self.limit

    def next_track(self):
        if self.cur_index >= len(self.tracks) and len(self.tracks) < self.total:
            self._get_more_tracks()

        if self.cur_index < len(self.tracks):
            track = self.tracks[self.cur_index]
            self.cur_index += 1
            return track
        else:
            return None


# Here's the pattern of a one to many:
class Fork:
    def __init__(self, source):
        pass

    def outputs(self):
        return []


class Split:
    def __init__(self, source, split_index):
        self.source = source
        self.split_index = split_index
        self.left_buffer = None
        self.right_buffer = None

    def _fill_buffer(self):
        if self.left_buffer == None:
            self.left_buffer = []
            self.right_buffer = []
            which = 0
            while True:
                track = self.source.next_track()
                if track:
                    if which < self.split_index:
                        self.left_buffer.append(track)
                    else:
                        self.right_buffer.append(track)
                else:
                    break
                which += 1

    class left_side:
        def __init__(self, outer):
            self.outer = outer
            self.name = 'first ' + str(outer.split_index) \
                + ' tracks of ' + outer.source.name

        def next_track(self):
            self.outer._fill_buffer()
            if len(self.outer.left_buffer) > 0:
                return self.outer.left_buffer.pop(0)
            else:
                return None

    class right_side:
        def __init__(self, outer):
            self.outer = outer
            self.name = 'After the first ' + str(outer.split_index) \
                + ' tracks of ' + outer.source.name

        def next_track(self):
            self.outer._fill_buffer()
            if len(self.outer.right_buffer) > 0:
                return self.outer.right_buffer.pop(0)
            else:
                return None

    def outputs(self):
        return [self.left_side(self), self.right_side(self)]

class TrackSource:
    def __init__(self, uris=[]):
        self.name = 'Tracks '
        self.uris = uris
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            results = spotify.tracks(self.uris)
            for track in results['tracks']:
                self.buffer.append(track['id'])
                tlib.add_track(self.name, track['id'], track)
            
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class AlbumSource:
    def __init__(self, name=None, uri=None):
        self.uri = uri
        self.name = 'Album ' + name
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            _,_,id = self.uri.split(':')
            results = spotify.album_tracks(id)
            for track in results['items']:
                self.buffer.append(track['id'])
                tlib.add_track(self.name, track['id'], track)

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class ArtistTopTracks:
    def __init__(self, name=None, uri=None):
        self.uri = uri
        self.name = 'Artist ' + name
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            _,_,id = self.uri.split(':')
            results = spotify.artist_top_tracks(id)
            for track in results['tracks']:
                self.buffer.append(track['id'])
                tlib.add_track(self.name, track['id'], track)

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class EchoNestPlaylist(object):
    def __init__(self, name, params):
        self.name = 'Echo Nest Playlist ' + name
        self.params = params
        self.buffer = None

        self.params['limit'] = True
        if 'bucket' not in self.params:
            self.params['bucket'] = []

        for bucket in en_song_buckets:
            self.params['bucket'].append(bucket)

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            response = en.get('playlist/static', **self.params)
            songs = response['songs']
            for song in songs:
                uri = song['tracks'][0]['foreign_id']
                self.buffer.append(uri_to_id(uri))
            tracks = tids_to_tracks(self.buffer)
            for song, track in zip(songs,tracks):
                track['en_song'] = tlib.flatten_en_song(song)
                if False:
                    pprint.pprint(track)
                    print
                    print
                tlib.add_track(self.name, track['id'], track)

        if len(self.buffer) > 0:
            tid = self.buffer.pop(0)
            return tid
        else:
            return None

class EchoNestGenreRadio():
    def __init__(self, genre, count):
        params = { 'type': 'genre-radio', 'genre': genre, 'results': count }
        self.enp = EchoNestPlaylist('Genre Radio for ' + genre, params)
        self.name = self.enp.name

    def next_track(self):
        return self.enp.next_track()

class EchoNestHottestSongs():
    def __init__(self, count):
        self.name = 'hotttest songs'

    def next_track(self):
        pass

class EchoNestArtistRadio():
    def __init__(self, artist, count):
        params = { 'type': 'artist-radio', 'artist': artist, 'results': count }
        self.enp = EchoNestPlaylist('Artist radio for ' + artist, params)
        self.name = self.enp.name

    def next_track(self):
        return self.enp.next_track()

class EchoNestArtistPlaylist():
    def __init__(self, artist, count):
        params = { 'type': 'artist', 'artist': artist, 'results': count }
        self.enp = EchoNestPlaylist('Artist playlist for ' + artist, params)
        self.name = self.enp.name

    def next_track(self):
        return self.enp.next_track()

class Looper:
    def __init__(self, source, max_size=200):
        self.name = 'looped ' + source.name
        self.source = source
        self.index = 0
        self.buffer = []
        self.looping = False
        self.max_size = max_size
        self.cur_size = 0

    def next_track(self):
        if self.cur_size >= self.max_size:
            return None

        if self.looping:
            if len(self.buffer) == 0:
                return None
            else:
                idx = self.index % len(self.buffer)
                self.index += 1
                track = self.buffer[idx]
        else:
            track = self.source.next_track()
            if track == None:
                self.looping = True
                return self.next_track()
            else:
                self.buffer.append(track)
        self.cur_size += 1
        return track

class Shuffler:
    def __init__(self, source):
        self.name = 'shuffled ' + source.name
        self.source = source
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling:    
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False
                random.shuffle(self.buffer)
        if len(self.buffer) > 0:
            return self.buffer.pop()
        else:
            return None

class First:
    def __init__(self, source, sample_size=10):
        self.name = 'first ' + str(sample_size) + ' of ' + source.name
        self.source = source
        self.sample_size = sample_size
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling and len(self.buffer) < self.sample_size:    
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False

            if len(self.buffer) >= self.sample_size:
                self.filling = False

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class Last:
    def __init__(self, source, sample_size=10):
        self.name = 'last ' + str(sample_size) + ' of ' + source.name
        self.source = source
        self.sample_size = sample_size
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling:
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False

        self.buffer = self.buffer[-self.sample_size:]
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class Reverse:
    def __init__(self, source, sample_size=10):
        self.name = 'reverse of ' + source.name
        self.source = source
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling:
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False

        if len(self.buffer) > 0:
            return self.buffer.pop()
        else:
            return None

class Sample:
    def __init__(self, source, sample_size=10):
        self.name = 'Sampling ' + str(sample_size) \
            + ' tracks from ' + source.name
        self.source = source
        self.sample_size = sample_size
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling:
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False
                random.shuffle(self.buffer)
                self.buffer = self.buffer[:self.sample_size]

        if len(self.buffer) > 0:
            return self.buffer.pop()
        else:
            return None

class Concatenate:
    def __init__(self, source_list):
        for s in source_list:
            print s.name
        self.name = 'concatenating ' + ' '.join([s.name for s in source_list])
        self.source_list = source_list
        self.index = 0

    def next_track(self):
        track = None
        while self.index < len(self.source_list):
            track = self.source_list[self.index].next_track()
            if track:
                break
            else:
                self.index += 1
        return track

class Alternate:
    def __init__(self, source_list):
        self.name = 'alternating ' + ' '.join([s.name for s in source_list])
        self.source_list = source_list
        self.index = 0

    def next_track(self):
        tries = len(self.source_list)
        while tries > 0:
            idx = self.index % len(self.source_list)
            self.index += 1
            track = self.source_list[idx].next_track()
            if track:
                return track
            else:
                tries -= 1
        return None


class AttributeFilter:
    def __init__(self, source, attr_get, match=None,min_val=None,max_val=None):
        self.name = source.name + ' filtered by ' + attr_get.name
        self.source = source
        self.attr_get = attr_get
        self.match = match
        self.min_val = min_val
        self.max_val = max_val
        self.match = match

    def next_track(self):
        while True:
            good = True
            track = self.source.next_track()
            if track:
                attr_val = self.attr_get(track)
                if self.match and attr_val != self.match:
                    good = False
                else:
                    if self.min_val and attr_val < self.min_val:
                        good = False
                    if self.max_val and attr_val > self.max_val:
                        good = False
            if good:
                break
        return track

def get_en_song(tid):
    uri = 'spotify:track:' + tid
    response = en.get('song/profile', track_id=uri, bucket=en_song_buckets)
    song = response['songs'][0]
    return tlib.flatten_en_song(song)

def en_attr(attr):
    def get(tid):
        track = tlib.get_track(tid)
        if not 'en_song' in track:
            track['en_song'] = get_en_song(tid)
        return track['en_song'][attr]
    get.name = 'en ' + attr
    return get

def sp_attr(attr):
    def get(tid):
        track = tlib.get_track(tid)
        return track[attr]
    get.name = 'en ' + attr
    return get

class TrackFilter:
    def __init__(self, source, filter):
        self.name = source.name + ' filtered by ' + filter.name
        self.source = source
        self.filter = filter
        self.bad_tracks = None
        self.debug = False

    def next_track(self):
        if self.bad_tracks == None:
            self.bad_tracks = set()
            while True:
                track = self.filter.next_track()
                if track:
                    self.bad_tracks.add(track)
                else:   
                    break
            
        while True:
            track = self.source.next_track()
            if track:
                if not track in self.bad_tracks:
                    return track
                else:
                    if self.debug:
                        print 'filtered out', tlib.get_tn(track)
            else:
                break
        return track

class Dumper:
    def __init__(self, source):
        self.name = 'dumper'
        self.source = source
        self.which = 1

    def next_track(self):
        track = self.source.next_track()
        if track:
            print self.which, tlib.get_tn(track)
            self.which += 1
        return track

class Debugger:
    def __init__(self, source):
        self.name = 'dumper'
        self.source = source

    def next_track(self):
        track = self.source.next_track()
        if track:
            tinfo = tlib.get_track(track)
            print json.dumps(tinfo, indent=4)
            print
        return track


def tids_to_tracks(tids):
    max_batch = 50
    start = 0
    out = []

    for start in xrange(0, len(tids), max_batch):
        ttids = tids[start:start+max_batch]
        results = spotify.tracks(ttids)
        out.extend(results['tracks'])
    return out

def runner(source, max_tracks = 500):
    pipe = Dumper(source)
    print 'running', source.name
    which = 0
    while which < max_tracks:
        track = pipe.next_track()
        if track:
            which += 1
        else:
            break

def uri_to_id(uri):
    return uri.split(':')[2]

uteen_party ='spotify:user:spotify:playlist:3MlpudZs4HT3i0yGPVfmHC'
ucoffee_house ='spotify:user:spotify:playlist:4BKT5olNFqLB1FAa8OtC8k'

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
    runner(both, 100)

def tester8():
    # Put the 10 random songs of teen party at the beginning of coffeehouse
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = Sample(PlaylistSource('Teen Party', uteen_party))
    both = Concatenate([teen, coffee])
    runner(both, 100)

def tester9():
    # The first 10 songs of coffee house in reverse order
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    pipe = Reverse(First(coffee))
    runner(pipe, 100)

def tester10():
    # sequence of 4 coffee house tracks followed by one of 4 randomly
    # selected teen party songs

    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = Sample(PlaylistSource('Teen Party', uteen_party), 4)
    pipe = Alternate([coffee] * 4 +  [Looper(teen)])
    runner(pipe, 100)

def tester11():
    # combine after foreer and the civil wars

    af = AlbumSource('after forever', 'spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
    vw = AlbumSource('The civil wars', 'spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
    pipe = Alternate([af, vw])
    runner(pipe, 100)

def tester12():
    # combine after forever and the civil wars, but lead with Katy Perry

    af = AlbumSource('after forever', 'spotify:album:0Gr8tHhOH8vzBTFqnf0YjT')
    vw = AlbumSource('The civil wars', 'spotify:album:5r0Xd2wqRkTE0BqbeYlnFN')
    kp = TrackSource(['spotify:track:5jrdCoLpJSvHHorevXBATy'])
    af_vw = Alternate([af, vw])
    pipe = Concatenate([kp, af_vw])
    runner(pipe, 100)

def tester13():
    # combine after forever and the civil wars, but lead with Katy Perry

    weezer = ArtistTopTracks('weezer', 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu')
    af = ArtistTopTracks('After Frver','spotify:artist:6ISyfZw4EVt16zhmH2lvxp')
    pipe = Shuffler(Concatenate([weezer, af]))
    runner(pipe, 100)

def tester14():
    params = { 
        'type': 'artist-radio',
        'artist': 'weezer',
        'results': 100
    }
    enr = EchoNestPlaylist('weezer radio', params)
    runner(enr, 100)


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
    runner(pipe, 100)

def tester16():
    # put first 10 songs of coffeehouse last
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    first, last = Split(coffee, 10).outputs()
    pipe = Concatenate([last, first])
    runner(pipe, 100)

def tester17():
    # play your fav coffeehouse but with 10 of the top 20 songs 
    # from teen party randomly mixed into the first 20 songs

    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    teen = PlaylistSource('Teen Party', uteen_party)

    steen = Sample(First(teen, 20), 10)
    first, last = Split(coffee, 10).outputs() 
    nfirst = Shuffler(Concatenate([steen, first]))
    pipe = Concatenate([nfirst, last])
    runner(pipe, 100)

def tester18():
    # create 10 song metal radio and then 10 song jazz radio
    metal = EchoNestGenreRadio('metal', 10)
    jazz = EchoNestGenreRadio('jazz', 10)
    pipe = Concatenate([metal, jazz])
    runner(pipe, 100)

def tester19():
    # create 10 song metal radio and then 10 song jazz radio and then 10 song
    # weezer radio and then 10 songs of after forever
    metal = EchoNestGenreRadio('metal', 10)
    jazz = EchoNestGenreRadio('jazz', 10)
    weezer = EchoNestArtistRadio('weezer', 10)
    af = EchoNestArtistPlaylist('after forever', 10)
    pipe = Concatenate([metal, jazz, weezer, af])
    runner(pipe, 100)

def tester20():
    # create 10 song metal radio and then 10 song jazz radio and then 10 song
    # weezer radio and then 10 songs of after forever
    metal = EchoNestGenreRadio('metal', 10)
    jazz = EchoNestGenreRadio('jazz', 10)
    weezer = EchoNestArtistRadio('weezer', 10)
    af = EchoNestArtistPlaylist('after forever', 10)
    pipe = Alternate([metal, jazz, weezer, af])
    runner(pipe, 100)

def tester21():
    metal = EchoNestGenreRadio('metal', 2)
    runner(Debugger(metal), 100)

def tester22():
    ''' find coffeehouse tracks with energy greater than .5
    '''
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    he = AttributeFilter(coffee, en_attr('energy'), min_val=.5)
    runner(Debugger(he), 100)

def tester23():
    ''' find coffeehouse tracks with duration less than 3 mins
    '''
    coffee = PlaylistSource('coffeehouse', ucoffee_house)
    he = AttributeFilter(coffee, sp_attr('duration_ms'), max_val=1000 * 60 * 3)
    runner(Debugger(he), 100)

if __name__ == '__main__':
    tester23()
    
