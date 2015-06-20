from pbl import *

'''
    dad and daughter agree that their morning drive playlist, should be split
    50/50 between classic jazz and teen party. Clever daughter gets her revenge
    by playling the most energetic brostep, juxtaposed against the quietest jazz
'''

if __name__ == '__main__':
    brostep = First(Sorter(EchoNestGenreRadio('brostep', 50), 'echonest.energy'), 5)
    cool_jazz = First(Sorter(EchoNestGenreRadio('cool jazz', 50), 'echonest.loudness'), 5)
    both = Alternate([brostep, cool_jazz])
    show_source(both, props=['echonest.loudness', 'echonest.energy', 'src'])


