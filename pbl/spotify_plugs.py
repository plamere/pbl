'''
    A set of sources and annotators for Spotify. An Spotify track has
    the following attributes::

        {
            "src": "Teen Party",
            "artist": "Various Artists",
            "title": "Walk The Moon - Teen Party Intro",
            "spotify": {
                "album": {
                    "album_type": "album",
                    "name": "Walk The Moon - Playlist Intros",
                    "external_urls": {
                        "spotify": "https://open.spotify.com/album/6ZQf8UHq907D9hu5amANXX"
                    },
                    "uri": "spotify:album:6ZQf8UHq907D9hu5amANXX",
                    "href": "https://api.spotify.com/v1/albums/6ZQf8UHq907D9hu5amANXX",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/1d06a0a9262a6634ca3a1cf9a9a0855b2245ba81",
                            "width": 640,
                            "height": 640
                        },
                        {
                            "url": "https://i.scdn.co/image/2d2dff2f132443083b4368ebead2c71d4dcd7eb7",
                            "width": 300,
                            "height": 300
                        },
                        {
                            "url": "https://i.scdn.co/image/c7aa8589b67593d3117020a5a0080598a5997785",
                            "width": 64,
                            "height": 64
                        }
                    ],
                    "type": "album",
                    "id": "6ZQf8UHq907D9hu5amANXX",
                    "available_markets": [ "AD", "...", ]
                },
                "name": "Walk The Moon - Teen Party Intro",
                "uri": "spotify:track:5oPzMRHjORXQlLemgpfacm",
                "external_urls": {
                    "spotify": "https://open.spotify.com/track/5oPzMRHjORXQlLemgpfacm"
                },
                "popularity": 5,
                "explicit": false,
                "preview_url": "https://p.scdn.co/mp3-preview/5e14b8b02dae9adf80f41fd0d4c03ca17002b939",
                "track_number": 2,
                "disc_number": 1,
                "href": "https://api.spotify.com/v1/tracks/5oPzMRHjORXQlLemgpfacm",
                "artists": [
                    {
                        "name": "Various Artists",
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/0LyfQWJT6nXafLPZqxe9Of"
                        },
                        "uri": "spotify:artist:0LyfQWJT6nXafLPZqxe9Of",
                        "href": "https://api.spotify.com/v1/artists/0LyfQWJT6nXafLPZqxe9Of",
                        "type": "artist",
                        "id": "0LyfQWJT6nXafLPZqxe9Of"
                    }
                ],
                "duration_ms": 7500,
                "external_ids": {},
                "type": "track",
                "id": "5oPzMRHjORXQlLemgpfacm",
                "available_markets": [ "AD", "AR", "...", ]
            },
            "duration": 7,
            "id": "5oPzMRHjORXQlLemgpfacm"
        }
'''
from track_manager import tlib
from engine import PBLException
import spotipy
import spotipy.util
import pprint


from spotipy.oauth2 import SpotifyClientCredentials

spotify = None
auth_sp = None



class PlaylistSource(object):
    '''
        A PBL source that generates a stream of tracks from the given Spotify
        playlist. If only a name is provided, the playlist will be searched for.
        Search success can be improved if the owner of the playlist is also
        provided.

        :param name: the name of the playlist
        :param uri: the uri of the playlist
        :param user: the owner of the playlist

    '''

    def __init__(self, name, uri=None, user=None):
        self.name = name
        self.uri = uri
        self.user = user

        self.next_offset = 0
        self.limit = 100

        self.tracks = []
        self.total = 1
        self.cur_index = 0


    def _get_uri_from_name(self, name):
        results = _get_spotify().search(q=name, type='playlist')
        if len(results['playlists']['items']) > 0:
            return results['playlists']['items'][0]['uri']
        else:
            return None

    def _get_uri_from_name_and_user(self, name, user):
        results = _get_spotify().user_playlists(user)
        while results:
            #pprint.pprint(results)
            #print
            for playlist in results['items']:
                if playlist['name'] == name:
                    return playlist['uri']
            if results['next']:
                results = _get_spotify().next(results)
            else:
                results = None
        return None

    def _get_more_tracks(self):
        _,_,user,_,playlist_id = self.uri.split(':')
        try:
            results = _get_spotify().user_playlist_tracks(user, playlist_id, 
                limit=self.limit, offset=self.next_offset)
        except spotipy.SpotifyException as e:
            raise PBLException(self, e.msg)

        self.total = results['total']
        for item in results['items']:
            track = item['track']
            self.tracks.append(track['id'])
            _add_track(self.name, track)
        self.next_offset += self.limit

    def next_track(self):
        if self.uri == None:
            if self.user:
                self.uri = self._get_uri_from_name_and_user(self.name, self.user)
            else:
                self.uri = self._get_uri_from_name(self.name)

            if not self.uri:
                msg = "Can't find playlist named " + self.name
                if self.user:
                    msg += ' for user ' + self.user
                raise PBLException(self, msg)

        if self.uri and self.cur_index >= len(self.tracks) \
            and len(self.tracks) < self.total:
            self._get_more_tracks()

        if self.cur_index < len(self.tracks):
            track = self.tracks[self.cur_index]
            self.cur_index += 1
            return track
        else:
            return None


class TrackSource(object):
    ''' A PBL Source that generates the a stream of tracks from the given list of
        URIs

        :param uris: a list of spotify track uris
    '''
    def __init__(self, uris=[]):
        self.name = 'Tracks '
        self.uris = uris
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            try:
                results = _get_spotify().tracks(self.uris)
            except spotipy.SpotifyException as e:
                raise PBLException(self, e.msg)
            for track in results['tracks']:
                if track and 'id' in track:
                    self.buffer.append(track['id'])
                    _add_track(self.name, track)
                else:
                    raise PBLException(self, 'bad track')
                
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class TrackSourceByName(object):
    ''' A PBL Source that generates a track given its artist and title

        :param title: the title and/or artist of the track
    '''
    def __init__(self, title):
        self.name = title 
        self.title = title
        self.uri = None

    def next_track(self):
        if self.uri == None:
            try:
                track = _find_track_by_name(_get_spotify(), self.title)
                if track and 'id' in track:
                    _add_track(self.name, track)
                    self.uri = track['id']
                    return self.uri
                else:
                    raise PBLException(self, "Can't find that track")
            except spotipy.SpotifyException as e:
                raise PBLException(self, e.msg)
        else:
            return None

class AlbumSource(object):
    '''
        A PBL Source that generates a series of tracks given an album

        :param title: the title of the album
        :param artist: the artist of the album
        :param uri: the URI of the album
    '''

    def __init__(self, title=None, artist=None, uri=None):
        self.uri = uri
        self.title = title
        self.artist = artist
        self.name = 'album ' + title if title != None else uri
        self.buffer = None

    def _get_uri_from_artist_title(self, artist, title):
        results = _get_spotify().search(q=title + ' ' + (artist if artist else ''), type='album')
        if len(results['albums']['items']) > 0:
            return results['albums']['items'][0]['uri']
        else:
            return None

    def next_track(self):
        if self.buffer == None:
            if self.title != None and self.uri == None:
                self.uri = self._get_uri_from_artist_title(self.artist, self.title)

            self.buffer = []
            if self.uri:
                _,_,id = self.uri.split(':')

                try:
                    results = _get_spotify().album_tracks(id)
                except spotipy.SpotifyException as e:
                    raise PBLException(self, e.msg)

                for track in results['items']:
                    self.buffer.append(track['id'])
                    _add_track(self.name, track)
            else:
                raise PBLException(self, "Can't find that album");

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class ArtistTopTracks(object):
    ''' A PBL Source that generates a series of top tracks by the given artist

        :param name: the name of the artist
        :param uri: the uri of the artist
    '''
    def __init__(self, name=None, uri=None):
        self.uri = uri
        self.name = 'Top tracks by ' + name
        self.artist_name = name
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []

            if self.uri == None:
                self.uri = _find_artist_by_name(_get_spotify(), self.artist_name)

            if self.uri != None:
                _,_,id = self.uri.split(':')
                try:
                    results = _get_spotify().artist_top_tracks(id)
                except spotipy.SpotifyException as e:
                    raise PBLException(self, e.msg)
                for track in results['tracks']:
                    self.buffer.append(track['id'])
                    _add_track(self.name, track)
            else:
                raise PBLException(self, "Can't find that artist")

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class PlaylistSave(object):
    ''' A PBL Sink that saves the source stream of tracks to the given playlist

        :param source: the source of tracks to be saved
        :param playlist_name: the name of the playlist
        :param user: the owner of the playlist
        :param uri: the uri of the playlist

    '''
    def __init__(self, source, playlist_name= None, user=None, uri=None, \
        create=False, append=False, max_size=100):
        self.source = source
        self.uri = uri
        self.user = user
        self.name = 'Spotify Save'
        self.playlist_name = playlist_name
        self.max_size = max_size
        self.append = append
        self.create = create
        self.buffer = []
        self.saved = False

    def next_track(self):
        track = self.source.next_track()
        if track and len(self.buffer) < self.max_size:
            self.buffer.append(track)
        elif not self.saved:
            self._save_playlist()
        return track

    def _save_playlist(self):
        self.saved = True
        if self.uri:
            _, _, user, _, pid = self.uri.split(':')
        else:
            user = self.user
            pid = None

        sp = _get_auth_spotify(user)
        if sp:
            if not pid:
                if self.playlist_name:
                    if self.create:
                        uri = None
                    else:
                        uri = _find_playlist_by_name(sp, self.user, self.playlist_name)
                    if uri:
                        print 'found', self.playlist_name, uri
                    else:
                        print 'creating new', self.playlist_name, 'playlist'
                        response = sp.user_playlist_create(self.user, self.playlist_name)
                        uri = response['uri']
                    pid =  uri.split(':')[4]
            if pid:
                batch_size = 100
                uris = [ 'spotify:track:' + id for id in self.buffer]
                for start in xrange(0, len(uris), batch_size):
                    turis = uris[start:start+batch_size]
                    if start == 0 and not self.append:
                        print 'replace', start
                        sp.user_playlist_replace_tracks(user, pid, turis)
                    else:
                        print 'add', start
                        sp.user_playlist_add_tracks(user, pid, turis)
        else:
            print "Can't get authenticated access to spotify"

def _get_spotify():
    global spotify
    if spotify == None:
        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        spotify.trace = False
    return spotify

def _get_auth_spotify(user):
    global auth_sp
    if auth_sp == None:
        scope = 'playlist-modify-public playlist-modify-private'
        token = spotipy.util.prompt_for_user_token(user, scope)
        if token:
            auth_sp = spotipy.Spotify(auth=token)

    return auth_sp


def _find_playlist_by_name(sp, user, name):
    batch_size = 50
    for start in xrange(0, 1000, batch_size):   
        playlists = sp.user_playlists(user, limit=batch_size, offset=start)
        for playlist in playlists['items']:
            if playlist['name'] == name:
                return playlist['uri']
    return None

def _find_artist_by_name(sp, name):
    results = _get_spotify().search(q=name, type='artist')
    if len(results['artists']['items']) > 0:
        return results['artists']['items'][0]['uri']
    else:
        return None

def _find_track_by_name(sp, name):
    results = _get_spotify().search(q=name, type='track')
    if len(results['tracks']['items']) > 0:
        return results['tracks']['items'][0]
    else:
        return None

def _annotate_tracks_with_spotify_data(tids):
    tids = tlib.annotate_tracks_from_cache('spotify', tids)
    if len(tids) > 0:
        print 'annotate tracks with spotify', tids
        results = _get_spotify().tracks(tids)
        for track in results['tracks']:
            tlib.annotate_track(track['id'], 'spotify', track)

def _add_track(source, track):
    dur = int(track['duration_ms'] / 1000.)
    tlib.make_track(track['id'], track['name'], 
                track['artists'][0]['name'], dur, source)
    tlib.annotate_track(track['id'], 'spotify', _flatten_track(track))

def _flatten_track(track):
    return track


_spotify_annotator = {
    'name': 'spotify',
    'annotator': _annotate_tracks_with_spotify_data,
    'batch_size': 50
}

tlib.add_annotator(_spotify_annotator)
