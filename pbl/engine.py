'''
    methods for running a PBL pipeline
'''
import standard_plugs

def run_source(source, max_tracks=40):
    '''
        pulls tracks from the given source

        :param source: the source of tracks
        :param max_tracks: the maximum number of tracks to pull
    '''
    count = 0
    for which in xrange(max_tracks):
        track = source.next_track()
        if not track:
            break
        else:
            count += 1
    return count



def get_tracks(source, max_tracks=40):
    '''
        pulls tracks from the given source and returns them

        :param source: the source of tracks
        :param max_tracks: the maximum number of tracks to pull
        :return: a list of tracks

    '''
    out = []
    for which in xrange(max_tracks):
        track = source.next_track()
        if not track:
            break
        else:
            out.append(track)
    return out

def show_source(source, ntracks = 100, props=[]):
    '''
        pulls tracks from the given source and displays them

        :param source: the source of tracks
        :param ntracks: the maximum number of tracks to pull
        :param props: properties to display
    '''
    print
    print source.name
    pipeline = standard_plugs.Dumper(source, props)
    try:
        run_source(pipeline, ntracks)
    except PBLException as e:
        print e
    print


class PBLException(Exception):
    def __init__(self, component, reason, cname=''):
        self.component = component
        self.reason = reason
        self.cname = cname
        print 'PBLException', component, reason, cname

    def __str__(self):
        if self.component:
            name = self.component.__class__.__name__ + ': "' + self.component.name + '"'
        else:
            name = self.cname
        return 'PBLException:' + name + '- ' + self.reason
