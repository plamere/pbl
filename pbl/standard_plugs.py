''' A set of standard sources, filters, sorters and sinks
'''
import random
import datetime
from track_manager import tlib
import json

class Annotator:
    ''' Annotates the tracks in a stream with external information

        :param source: the source of tracks
        :param type: the type of annotation (spotify, echonest)
    '''
    def __init__(self, source, type):
        self.annotator = tlib.get_annotator(type)
        self.name = source.name + ' annotated with ' + type +  ' data'
        self.source = source
        self.buffer = []
        self.fillbuf = []

    def next_track(self):
        while len(self.fillbuf) < self.annotator['batch_size']:
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
                tinfo = tlib.get_track(track)
                if type not in tinfo:
                    self.fillbuf.append(track)
            else:
                break
        if len(self.fillbuf) > 0:
            self._fetch_fillbuf()

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

    def _fetch_fillbuf(self):
        self.annotator['annotator'](self.fillbuf)
        self.fillbuf = []

class FakeTrackSource:
    '''
        Generates a series of fake tracks, suitable for testing

        param: count: the number of tracks to generate

    '''
    def __init__(self, count=10):
        self.name = 'FakeTracks'
        self.count = count
        self.fake_id = 1000000

    def next_track(self):
        track = None
        if self.count > 0:
            track = tlib.make_track(self._fake_id(), 
                self._fake_name(), self._fake_name(), 180, 'FakeTrackSource')
            self.count -= 1
        return track


    def _fake_id(self):
        self.fake_id += 1
        return str(self.fake_id)

    def _fake_name(self):
        nouns = 'vixen bear dog cat waters drums parade fire france'
        adjectives = 'frumpy cold wet fast red jumpy strange weird nifty'

        adj = random.choice(adjectives.split())
        noun = random.choice(nouns.split())
        return ' '.join([adj, noun])


class Split:
    '''
        Splits a stream into two streams

        :param source: the source of the track stream
        :param split_index: the index where the split occurs
    '''

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


class Looper:
    '''
        Given a source, generate a stream of a given size by circulating through
        the tracks in the source

        :param source: the stream source
        :param max_size: the number of tracks returned

    '''
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
    ''' Shuffles the tracks in the stream

        :param source: the source of tracks
        :param max_size: the maximum number of tracks to return
    '''
    def __init__(self, source, max_size=0):
        self.name = 'shuffled ' + source.name
        self.source = source
        self.buffer = []
        self.filling = True
        self.max_size = max_size

    def next_track(self):
        while self.filling:    
            track = self.source.next_track()
            if track and (self.max_size == 0 or len(self.buffer) < self.max_size):
                self.buffer.append(track)
            else:
                self.filling = False
                random.shuffle(self.buffer)
        if len(self.buffer) > 0:
            return self.buffer.pop()
        else:
            return None

class DeDup:
    '''
        Remove any duplicate tracks in the stream

        :param source: the stream source
        :param by_name: if True match by track ID and name

    '''

    def __init__(self, source, by_name = False):
        self.name = 'dedupped ' + source.name
        self.source = source
        self.by_name = by_name
        self.history = set()

    def next_track(self):
        track = None
        while True:
            track = self.source.next_track()
            if self.by_name:
                tname = tlib.get_tn(track).lower()
                if tname in self.history:
                    continue
                else:
                    self.history.add(tname)

            if track in self.history:
                continue
            else:
                self.history.add(track)
                break

        return track

class Buffer:
    '''
        Buffer up the given number of tracks

        :param source: the stream source
        :param max_size: the size of the buffer
    '''
    def __init__(self, source, max_size=40):
        self.name = 'buffered ' + source.name
        self.source = source
        self.buffer = []
        self.filling = True
        self.max_size = max_size

    def next_track(self):
        while self.filling:    
            track = self.source.next_track()
            if track and (self.max_size == 0 or len(self.buffer) < self.max_size):
                self.buffer.append(track)
            else:
                self.filling = False

        if len(self.buffer) > 0:
            return self.buffer.pop()
        else:
            return None

class LongerThan:
    '''
        Limit the stream, if possible, to tracks with a duration that is longer
        than the given time

        :param source: the source stream
        :param time: the time in seconds
    '''
    def __init__(self, source, time=1200):
        self.name = 'LongerThan ' + str(time) + ' secs'
        self.source = source
        self.time = time
        self.cur_time = 0

    def next_track(self):
        if self.cur_time > self.time:
            return None
        else:
            track = self.source.next_track()
            if track:
                duration = tlib.get_attr(track, 'duration')
                self.cur_time += duration
            return track

class ShorterThan:
    '''
        Limit the stream, if possible, to tracks with a duration that is just
        shorter than the given time

        :param source: the source stream
        :param time: the time in seconds
    '''
    def __init__(self, source, time=1200):
        self.name = 'Shorter Than ' + str(time) + ' secs'
        self.source = source
        self.time = time
        self.cur_time = 0

    def next_track(self):
        if self.cur_time >= self.time:
            return None
        else:
            track = self.source.next_track()
            if track:
                duration = tlib.get_attr(track, 'duration')
                self.cur_time += duration
                if self.cur_time >= self.time:
                    return None
            return track

class Sorter:
    '''
        Sorts the tracks in the given stream by the given attribute

        :param source: the source of the tracks
        :param attr: the attribute to be sorted
        :param reverse: if True reverse the sort
        :param max_size: maximum tracks to sort
    '''
        
    def __init__(self, source, attr, reverse=False, max_size=0):
        self.name = source.name + ' sorted by ' + attr + ('(reverse)' if reverse else '')
        self.source = source
        self.buffer = []
        self.filling = True
        self.max_size = max_size
        self.attr = attr
        self.reverse = reverse

    def next_track(self):
        while self.filling:    
            track = self.source.next_track()
            if track and (self.max_size == 0 or len(self.buffer) < self.max_size):
                self.buffer.append(track)
            else:
                self.filling = False
                self.buffer.sort(reverse=self.reverse, key=lambda tid: tlib.get_attr(tid, self.attr))
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class CustomSorter:
    '''
        Sorts the tracks by a custom key

        :param source: the source of the tracks
        :param keyfunc: function that turns a track id into the sort key
        :param reverse: if True reverse the sort
        :param max_size: maximum tracks to sort
    '''
    def __init__(self, source, keyfunc, reverse=False, max_size=0):
        self.name = source.name + ' custom sorted'
        self.source = source
        self.keyfunc = keyfunc
        self.buffer = []
        self.filling = True
        self.max_size = max_size
        self.reverse = reverse

    def next_track(self):
        while self.filling:    
            track = self.source.next_track()
            if track and (self.max_size == 0 or len(self.buffer) < self.max_size):
                self.buffer.append(track)
            else:
                self.filling = False
                self.buffer.sort(reverse=self.reverse, key=self.keyfunc)
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class First:
    '''
        Returns the first tracks from a stream

        :param source: the source of tracks
        :param sample_size: the number of tracks to return
    '''
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
    '''
        Returns the last tracks from a stream

        :param source: the source of tracks
        :param sample_size: the number of tracks to return
    '''
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
    '''
        Reverses the order of the tracks in the stream

        :param source: the source of tracks
    '''
    def __init__(self, source):
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
    '''
        Randomly sample tracks from the stream

        :param source: the source of tracks
        :param sample_size: the number of tracks to return
    '''
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
    '''
        Concatenate multiple streams

        :param source: the source of tracks
        :param source_list: a list of sources
    '''
    def __init__(self, source_list):
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
    '''
        Alternate tracks from  multiple streams

        :param source: the source of tracks
        :param source_list: a list of sources
    '''
    def __init__(self, source_list):
        self.name = 'alternating between ' + ', '.join([s.name for s in source_list])
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

class Conditional:
    '''
        Alternate tracks from  two streams based on a conditional

        :param source: the source of tracks
        :param cond_func: a function that returns a boolean
        :param trueSource: source of tracks when conf_func returns True
        :param falseSource: source of tracks when conf_func returns False
    '''
    def __init__(self, cond_func, trueSource, falseSource):
        self.name = 'Conditional of ' + ' '.join([trueSource.name, falseSource.name])
        self.trueSource = trueSource
        self.falseSource = falseSource
        self.cond_func = cond_func

    def next_track(self):
        if self.cond_func():
            return self.trueSource.next_track()
        else:
            return self.falseSource.next_track()

class Case:
    '''
        Selects tracks from streams based upon a mapping function

        :param source: the source of tracks
        :param func: a function that returns the source_map key
        :param source_map: a may of key to source streams
    '''

    def __init__(self, func, source_map):

        def default_behavior():
            return None

        self.name = 'Case of ' + ', '.join([n +':' + s.name for n,s in source_map.items()])
        self.source_map = source_map
        self.func = func
        if not 'default' in self.source_map:
            self.source_map['default'] = default_behavior

    def next_track(self):
        key = self.func()
        if not key in self.source_map:
            key = 'default'
        source = self.source_map[key]
        return source.next_track()

'''
  Some handy dandy conditional funcs
'''

def is_day_of_week(day_of_week):
    ''' checks if cur day is given day of the week

        :param day_of_week: Monday is 0 and Sunday is 6.
    '''
    def cond_func():
        return datetime.datetime.today().weekday() == day_of_week
    return  cond_func

def get_simple_day_part():
    '''
        returns the daypart
    '''
    hour = datetime.datetime.today().hour
    if hour < 12:
        return 'morning'
    elif hour < 18:
        return 'afternoon'
    elif hour < 22:
        return 'evening'
    else:
        return 'night'


class AttributeRangeFilter:
    '''
        Filters tracks based upon range check of an attribute

        :param source: the source of tracks
        :param attr: the attribute of interest
        :param match: if not None, attribute value must match this exactly
        :param min_val: if not None, attribute value must be at least this
        :param max_val: if not None, attribute value must be no more than this
    '''
    def __init__(self, source, attr, match=None,min_val=None,max_val=None):
        self.name = source.name + ' filtered by ' + attr
        self.source = source
        self.attr = attr
        self.match = match
        self.min_val = min_val
        self.max_val = max_val
        self.match = match

    def next_track(self):
        while True:
            good = True
            track = self.source.next_track()
            if track:
                attr_val = tlib.get_attr(track, self.attr)
                if attr_val == None:
                    good = False
                elif self.match and attr_val != self.match:
                    good = False
                else:
                    if self.min_val and attr_val < self.min_val:
                        good = False
                    if self.max_val and attr_val > self.max_val:
                        good = False
            if good:
                break
        return track


class TrackFilter:
    '''
        Removes tracks from the stream based on a second stream

        :param source: the source of tracks
        :param filter: the stream of bad tracks to be removed
    '''
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

class ArtistFilter:
    '''
        Removes tracks from the stream that have the given artists

        :param source: the source of tracks
        :param artistNames: the names of the artists to be removed
    '''
    def __init__(self, source, artistNames):
        self.name = source.name + ' with songs by ' + ', '.join(artistNames) + ' removed'
        self.source = source
        self.bad_artists = set(artistNames)
        self.debug = False

    def next_track(self):
            
        while True:
            track = self.source.next_track()
            if track:
                tinfo = tlib.get_track(track)
                if tinfo['artist'] not in self.bad_artists:
                    return track
                else:
                    if self.debug:
                        print 'filtered out', tlib.get_tn(track)
            else:
                break
        return track

class Dumper:
    '''
        Dumps tracks to the terminal

        :param source: the source of tracks
        :param props: list of property names to be included in the dump
    '''
        
    def __init__(self, source, props):
        self.name = 'dumper'
        self.source = source
        self.which = 1
        self.props = props

    def next_track(self):
        track = self.source.next_track()
        if track:
            print self.which, tlib.get_tn(track)
            if len(self.props) > 0:
                for prop in self.props:
                    val = tlib.get_attr(track, prop)
                    if val != None:
                        print '   ', prop, '->', val
            self.which += 1
        return track

class Debugger:
    '''
        Shows details on each track in the stream

        :param source: the source of tracks
    '''


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

class SaveToJson:
    '''
        Saves the stream to json
        :param source: the source of tracks
        :param name: the name of the json file
        :param max_size: the max tracks to save
    '''
    def __init__(self, source, name='playlist.json', max_size=100):
        self.name = 'SaveToJson ' + name
        self.source = source
        self.playlist_name = name
        self.max_size = max_size
        self.saved = False
        self.buffer = []

    def next_track(self):
        track = self.source.next_track()
        if track and len(self.buffer) < self.max_size:
            self.buffer.append(track)
        elif not self.saved:
            self._save_playlist()
        return track

    def _save_playlist(self):
        self.saved = True
        f = open(self.playlist_name, 'w')
        out = []
        for tid in self.buffer:
            t = tlib.get_track(tid)
            if t:
                out.append(t)
            
        print >> f, json.dumps(out, indent=4)
        f.close()
