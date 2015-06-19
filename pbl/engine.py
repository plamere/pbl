import standard_plugs

def run_source(source, max_tracks=40):
    count = 0
    for which in xrange(max_tracks):
        track = source.next_track()
        if not track:
            break
        else:
            count += 1
    return count



def get_tracks(source, max_tracks=40):
    out = []
    for which in xrange(max_tracks):
        track = source.next_track()
        if not track:
            break
        else:
            out.append(track)
    return out

def show_source(source, ntracks = 100, props=[]):
    print
    print source.name
    pipeline = standard_plugs.Dumper(source, props)
    run_source(pipeline, ntracks)
    print

