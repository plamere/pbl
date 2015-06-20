import requests
import random
from track_manager import tlib

class BoilTheFrogSource:
    '''
        a PBL source that generates a list of tracks that gradually go from the
        starting artist to the ending artist

        :param start: the starting artist
        :param end: the ending artist

    '''

    def __init__(self, start, end=None):
        self.name = 'Path from ' + start + ' to ' + end
        self.start = start
        self.end = end
        self.tracks = None

    def next_track(self):
        if self.tracks == None:
            self.tracks = self._get_path(self.start, self.end)

        if len(self.tracks) > 0:
            return self.tracks.pop(0)
        else:
            return None

    def _get_path(self, start, end):
        params = {
            'start' : start,
            'end' : end
        }
        response = requests.get('http://labs2.echonest.com/ArtistGraphServer/find_path', 
            params=params)

        js = response.json()

        tracks = []
        for artist in js['path']:
            track = random.choice(artist['songs'])
            tid = 'spotify:track:' + track['id']
            # TODO fix duration here
            tlib.make_track(tid, track['title'], artist['name'], 180, 'frog')
            tracks.append(tid)
        return tracks

