from track_manager import tlib
import spotipy
import spotipy.util
import pprint


from spotipy.oauth2 import SpotifyClientCredentials
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
spotify.trace = False

class PlaylistSource:

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
        results = spotify.search(q=name, type='playlist')
        if len(results['playlists']['items']) > 0:
            return results['playlists']['items'][0]['uri']
        else:
            return None

    def _get_uri_from_name_and_user(self, name, user):
        results = spotify.user_playlists(user)
        while results:
            #pprint.pprint(results)
            #print
            for playlist in results['items']:
                if playlist['name'] == name:
                    return playlist['uri']
            if results['next']:
                results = spotify.next(results)
            else:
                results = None
        return None

    def _get_more_tracks(self):
        _,_,user,_,playlist_id = self.uri.split(':')
        results = spotify.user_playlist_tracks(user, playlist_id, 
            limit=self.limit, offset=self.next_offset)

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

        if self.uri and self.cur_index >= len(self.tracks) and len(self.tracks) < self.total:
            self._get_more_tracks()

        if self.cur_index < len(self.tracks):
            track = self.tracks[self.cur_index]
            self.cur_index += 1
            return track
        else:
            return None


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
                _add_track(self.name, track)
            
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class AlbumSource:
    def __init__(self, title=None, artist=None, uri=None):
        self.uri = uri
        self.title = title
        self.artist = artist
        self.name = 'album ' + title if title != None else uri
        self.buffer = None

    def _get_uri_from_artist_title(self, artist, title):
        results = spotify.search(q=title + ' ' + (artist if artist else ''), type='album')
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
                results = spotify.album_tracks(id)
                for track in results['items']:
                    self.buffer.append(track['id'])
                    _add_track(self.name, track)

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class ArtistTopTracks:
    def __init__(self, name=None, uri=None):
        self.uri = uri
        self.name = 'Top tracks by ' + name
        self.artist_name = name
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []

            if self.uri == None:
                self.uri = _find_artist_by_name(spotify, self.artist_name)

            if self.uri != None:
                _,_,id = self.uri.split(':')
                results = spotify.artist_top_tracks(id)
                for track in results['tracks']:
                    self.buffer.append(track['id'])
                    _add_track(self.name, track)

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class PlaylistSave:
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

auth_sp = None

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
    results = spotify.search(q=name, type='artist')
    if len(results['artists']['items']) > 0:
        return results['artists']['items'][0]['uri']
    else:
        return None
    

def _annotate_tracks_with_spotify_data(tids):
    results = spotify.tracks(tids)
    for track in results['tracks']:
        tlib.annotate_track(track['id'], 'spotify', track)

def _add_track(source, track):
    tlib.make_track(track['id'], track['name'], 
                track['artists'][0]['name'], source)
    tlib.annotate_track(track['id'], 'spotify', _flatten_track(track))

def _flatten_track(track):
    return track


_spotify_annotator = {
    'name': 'spotify',
    'annotator': _annotate_tracks_with_spotify_data,
    'batch_size': 50
}

tlib.add_annotator(_spotify_annotator)
