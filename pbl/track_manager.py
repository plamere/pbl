
import os

if os.environ.get('PBL_NO_CACHE'):
    import nocache as cache
else:
    import cache

class TrackLibrary(object):
    ''' manages track attributes
    '''
    
    def __init__(self):
        self.tmap = { }
        self.annotators = {}
        self.missing_annotator_reported = False

    def add_track(self, source_name, tid, info):
        ''' Adds a track to the library

            :param source_name: the name of the track source
            :param tid: the track id
            :param info: the track info
        '''
        info['src'] = source_name
        self.tmap[tid] = info


    def annotate_tracks_from_cache(self, type, tids):
        out = []
        for tid in tids:
            song = cache.get(type, tid)
            if song:
                self.annotate_track(tid, type, song, add_to_cache=False)
            else:
                out.append(tid)
        return out

    def add_annotator(self, annotator):
        self.annotators[annotator['name']] = annotator

    def get_annotator(self, name):
        return self.annotators[name]

    def get_track(self, tid):
        ''' gets the track info

            :param tid: the track id
        '''
        return self.tmap[tid]

    def get_tn(self, tid):
        track = self.get_track(tid)
        if track:
            return track['title'] + ' -- ' + track['artist']
        else:
            return '(none)'

    def make_track(self, id, title, artist, dur, source):
        track = {
            'id': id,
            'title': title,
            'artist': artist,
            'duration': dur,
            'src': source
        }
        self.tmap[id] = track
        return id

    def annotate_track(self, tid, name, data, add_to_cache=True):
        track = self.get_track(tid)
        if track:
            track[name] = data
            if add_to_cache and cache.get(name, tid) == None:
                cache.put(name, tid, data)
        else:
            print "can't annotate missing track", tid

    def get_attr(self, tid, attr):
        '''
            Gets the value of the given attribute for a track

            :param tid: the track id
            :param attr: the attribte name

        '''
        # currently support 'attribute' or 'pkg.attribute'
        track = self.get_track(tid)
        if track:
            fields = attr.split('.')
            if len(fields) == 1:
                attr = fields[0]
                if attr in track:
                    return track[attr]
            elif len(fields) == 2:
                type, attr = fields
                if not type in track and type in self.annotators:
                    if self.annotators[type]['batch_size'] > 1 and not self.missing_annotator_reported:
                        print 'last minute fetch of', type, 'info for', tid
                        print 'consider adding an annotator to speed things up'
                        self.missing_annotator_reported = True
                    self.annotators[type]['annotator']([tid])
                if type in track:
                    type_info = track[type]
                    if type_info and attr in type_info:
                        return type_info[attr]
            else:
                print 'bad attr path', attr

        return None
            

tlib = TrackLibrary()

