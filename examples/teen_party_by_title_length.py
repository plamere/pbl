from  pbl import *

tp = CustomSorter(PlaylistSource('Teen Party'), 
    lambda tid: len(tlib.get_attr(tid, 'title') + tlib.get_attr(tid, 'artist')))
show_source(tp)
