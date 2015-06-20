from pbl import *

'''
    Dump out a single track to show the available attributes on an 
    Echo Nest Track
'''

if __name__ == '__main__':
    show_source(Debugger(EchoNestArtistRadio('weezer', 1)))
