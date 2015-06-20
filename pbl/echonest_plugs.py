from track_manager import tlib
import utils
import pprint
import pyen

en = pyen.Pyen()
en.trace=True

_en_song_buckets = [
    'id:spotify', 'audio_summary', 'song_hotttnesss_rank', 'song_hotttnesss',
    'song_currency_rank', 'song_currency', 'artist_hotttnesss', 'tracks',
    'artist_familiarity', 'artist_discovery'
]

class EchoNestPlaylist(object):
    '''
        A track source that uses the Echo Nest playlist API to generate tracks
    '''
    def __init__(self, name, params):
        '''
            create an EchoNestPlaylist source.

            :param name: the name of the source
            :param params: a dictionary of params (see the Echo Nest
            playlist/static documentation for a full list of available
            paramaters.
        '''
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
            response = en.get('playlist/static', **self.params)
            for song in response['songs']:
                id = _add_song(self.name, song)
                self.buffer.append(id)

        if len(self.buffer) > 0:
            tid = self.buffer.pop(0)
            return tid
        else:
            return None


class EchoNestGenreRadio():
    '''
        A genre radio source
    '''
    def __init__(self, genre, count):
        '''
            :param :genre the genre of interest
            :param :count the number of tracks to generate
        '''
        params = { 'type': 'genre-radio', 'genre': genre, 'results': count }
        self.enp = EchoNestPlaylist('Genre Radio for ' + genre, params)
        self.name = self.enp.name

    def next_track(self):
        return self.enp.next_track()

class EchoNestHottestSongs():
    '''
        Returns the set of hotttest songs from the Echo Nest
    '''
    def __init__(self, count):
        '''
            :param :count the number of tracks to generate
        '''
        self.name = 'hotttest songs'

    def next_track(self):
        pass

class EchoNestArtistRadio():
    '''
        A PBL source that generates a stream of tracks that are by
        the given artist or similar artists
    '''
    def __init__(self, artist, count):
        '''
            :param :artist the name of the artist
            :param :count the number of tracks to generate
        '''

        params = { 'type': 'artist-radio', 'artist': artist, 'results': count }
        self.enp = EchoNestPlaylist('Artist radio for ' + artist, params)
        self.name = self.enp.name

    def next_track(self):
        return self.enp.next_track()

class EchoNestArtistPlaylist():
    '''
        A PBL source that generates a stream of tracks by the given
        artist
    '''
    def __init__(self, artist, count):
        '''
            :param :artist the name of the artist
            :param :count the number of tracks to generate
        '''
        params = { 'type': 'artist', 'artist': artist, 'results': count }
        self.enp = EchoNestPlaylist('Artist playlist for ' + artist, params)
        self.name = self.enp.name

    def next_track(self):
        return self.enp.next_track()

def _annotate_tracks_with_echonest_data(tids):
    stids = set(tids)
    uris = [ 'spotify:track:' + tid for tid in tids]
    try:
        response = en.get('song/profile', track_id=uris, bucket=_en_song_buckets)
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
    except pyen.PyenException:
        print 'annotate_tracks_with_echonest_data:no info for', tids
        pass


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

tlib.add_annotator(_echonest_annotator)
