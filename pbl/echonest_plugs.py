'''
    A set of sources and annotators for Echo Nest API. An Echo Nest track has
    the following attributes::

        {
            "src": "Echo Nest Playlist Artist radio for weezer",
            "artist": "Weezer",
            "title": "Perfect Situation",
            "id": "3oM0sxN8FZwgUvccT9n34d",
            "duration": 255,
            "echonest": {
                "album_type": "unknown",
                "artist_discovery": 0.3328849845870755,
                "speechiness": 0.035816,
                "duration": 255.37288,
                "id": "SOZKJDU1461E3C9B6E",
                "title": "Perfect Situation",
                "acousticness": 0.03422,
                "danceability": 0.452168,
                "song_currency": 0.017234941438929167,
                "artist_familiarity": 0.812078,
                "artist_id": "AR633SY1187B9AC3B9",
                "energy": 0.791129,
                "song_hotttnesss": 0.391096,
                "tempo": 93.946,
                "artist_name": "Weezer",
                "instrumentalness": 0.000311,
                "key": 6,
                "audio_md5": "dca9daa0723096d6ed7a5507b1bca17e",
                "album_name": "Make Believe",
                "album_date": "2005-05-09",
                "liveness": 0.135915,
                "artist_hotttnesss": 0.72962,
                "mode": 1,
                "time_signature": 4,
                "loudness": -4.131,
                "valence": 0.37193
            }
        }
'''

from track_manager import tlib
from engine import PBLException
import utils
import pprint
import pyen

en = None
debug = False

_en_song_buckets = [
    'id:spotify', 'audio_summary', 'song_hotttnesss',
    'song_currency', 'artist_hotttnesss', 'tracks',
    'artist_familiarity', 'artist_discovery'
]



class EchoNestPlaylist(object):
    '''
        A track source that uses the Echo Nest playlist API to generate tracks

        :param name: the name of the source
        :param params: a dictionary of params (see the Echo Nest
         playlist/static documentation for a full list of available
         parameters.
    '''
    def __init__(self, name, params):
        self.name = 'Echo Nest Playlist ' + name
        self.params = params
        self.buffer = None

        self.params['limit'] = True
        if 'bucket' not in self.params:
            self.params['bucket'] = []

        for bucket in _en_song_buckets:
            self.params['bucket'].append(bucket)

    def next_track(self):
        '''
            returns the next track in the stream
        '''
        if self.buffer == None:
            self.buffer = []
            try:
                response = _get_en().get('playlist/static', **self.params)
            except pyen.PyenException as e:
                raise PBLException(self, e.msg)

            for song in response['songs']:
                id = _add_song(self.name, song)
                self.buffer.append(id)

        if len(self.buffer) > 0:
            tid = self.buffer.pop(0)
            return tid
        else:
            return None

class EchoNestGenreRadio(EchoNestPlaylist):
    '''
        A genre radio track source

        :param genre: the genre of interest
        :param count: the number of tracks to generate
    '''
    def __init__(self, genre, count):
        '''
        '''
        params = { 'type': 'genre-radio', 'genre': genre.lower(), 'results': int(count) }
        super(EchoNestGenreRadio, self).__init__('Genre radio for ' + genre, params)


class EchoNestHottestSongs(object):
    '''
        Returns the set of hotttest songs from the Echo Nest. TBD
        :param count: the number of tracks to generate
    '''

    def __init__(self, count):
        self.name = 'hotttest songs'

    def next_track(self):
        pass

class EchoNestArtistRadio(EchoNestPlaylist):
    '''
        A PBL source that generates a stream of tracks that are by
        the given artist or similar artists

        :param artist: the name of the artist
        :param count: the number of tracks to generate
    '''
    def __init__(self, artist, count):
        params = { 'type': 'artist-radio', 'artist': artist, 'results': int(count) }
        super(EchoNestArtistRadio, self).__init__('Artist radio for ' + artist, params)

class EchoNestArtistPlaylist(EchoNestPlaylist):
    '''
        A PBL source that generates a stream of tracks by the given
        artist

        :param artist: the name of the artist
        :param count: the number of tracks to generate
    '''
    def __init__(self, artist, count):
        params = { 'type': 'artist', 'artist': artist, 'results': int(count) }
        super(EchoNestArtistPlaylist, self).__init__('Artist playlist for ' + artist, params)


def _annotate_tracks_with_echonest_data(tids):
    otids = tlib.annotate_tracks_from_cache('echonest', tids)
    if len(otids) > 0:
        stids = set(otids)
        uris = [ 'spotify:track:' + tid for tid in otids]
        try:
            if debug:
                print 'getting echonest info for', otids
            response = _get_en().get('song/profile', track_id=uris, bucket=_en_song_buckets)
            res = set()
            for song in response['songs']:
                for track in song['tracks']:
                    tid = utils.uri_to_id(track['foreign_id'])
                    if tid in stids:
                        res.add(tid)
                        tlib.annotate_track(tid, 'echonest', _flatten_en_song(song, tid))
            diff = stids - res
            if len(diff) > 0:
                pass
                #print 'requested', len(stids), 'collected', len(res)
        except pyen.PyenException as e:
            print 'annotate_tracks_with_echonest_data:no info for', otids
            print 'echonest error', e.http_status, e.code, e.msg
            for tid in otids:
                tlib.annotate_track(tid, 'echonest', {'empty': 'empty'})
    

def _flatten_en_song(song, id):
    for k,v in song['audio_summary'].items():
        song[k] = v

    if 'artist_foreign_ids' in song:
        del song['artist_foreign_ids']

    if 'audio_summary' in song:
        del song['audio_summary']

    if 'analysis_url' in song:
        del song['analysis_url']

    for track in song['tracks']:
        tid = utils.uri_to_id(track['foreign_id'])
        if id == tid:
            if 'album_name' in track:
                song['album_name'] = track['album_name']
            if 'album_date' in track:
                song['album_date'] = track['album_date']
            if 'album_type' in track:
                song['album_type'] = track['album_type']

    del song['tracks']
    return song

def _add_song(source, song):
    id = utils.uri_to_id(song['tracks'][0]['foreign_id'])
    dur = int(song['audio_summary']['duration'] )
    tlib.make_track(id, song['title'], song['artist_name'], dur, source)
    tlib.annotate_track(id, 'echonest', _flatten_en_song(song, id))
    return id

_echonest_annotator = {
    'name': 'echonest',
    'annotator': _annotate_tracks_with_echonest_data,
    'batch_size': 50
}

def _get_en():
    global en
    if en == None:
        en = pyen.Pyen()
        en.trace = False
    return en

tlib.add_annotator(_echonest_annotator)
