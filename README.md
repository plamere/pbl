# Playlist Builder Library (PBL) 
The Playlist Builder Library (PBL) is a Python library that you can use to create playlists. 

## Documentation
PBL's full documentation is online at [PBL Documentation](http://pbl.readthedocs.org/) 

## A Quick Example
For example, let's say you like to listen to music on your morning commute. You mostly like to listen to classic rock, but you don't want to get too out of touch with new music so you'd like a little bit of new music thrown in as well. With PBL you can easily create a such a playlist like so:

```python 
from pbl import *

classic_rock = Sample(PlaylistSource('Rock Classics'), sample_size=10)
new_music = Sample(PlaylistSource('New Music Tuesday'), sample_size=5)
combined = Shuffler(Concatenate([classic_rock, new_music]))
show_source(combined)
```

This program grabs the 'Rock Classics' playlist from Spotify (by searching for the most popular playlist on Spotify with that name), and randomly samples 10 tracks from it. Similarly it randomly samples 5 tracks from the 'New Music Tuesday' playlist. It concatentates these two playlists together and shuffles them. Here's the resulting output:

```
    1 Chop Suey! -- System Of A Down
    2 Sweet Child O' Mine -- Guns N' Roses
    3 Dust in the Wind -- Kansas
    4 Dawkins Christ -- Refused
    5 Born in the U.S.A. -- Bruce Springsteen
    6 Slowly -- Dropout
    7 All Along The Watchtower -- Jimi Hendrix
    8 Eye of the Tiger -- Survivor
    9 My Kind -- Hilary Duff
    10 White Knuckles -- Boh Doran
    11 Something Like Happiness -- The Maccabees
    12 Owner Of A Lonely Heart -- Yes
    13 Don't Stop Believin' -- Journey
    14 Africa -- Toto
    15 Lola - Remastered -- The Kinks
```

As you can see, that's 15 songs, 5 are new, and 10 are classic.
The function __show_source__ shows the playlist in the terminal, but of course to listen to a playlist, it needs to be saved on Spotify. We can do that by adding a **PlaylistSave** call like so:


```python 
from pbl import *

classic_rock = Sample(PlaylistSource('Rock Classics'), sample_size=10)
new_music = Sample(PlaylistSource('New Music Tuesday'), sample_size=5)
combined = Shuffler(Concatenate([classic_rock, new_music]))
combined = PlaylistSave(combined, 'my morning commute', 'plamere')
show_source(combined)
```
Now, whenever the program is run, my 'my morning commute' playlist will be updated with a different set of tracks sampled from Rock Classics and New Music Tuesday.

## Quick Start
To get started, install __pbl__ with:

```
% pip install pbl
```

this should take care of all the dependencies (including spotipy, pyen and others).

Once installed, just __import pbl__ and you'll have everything you need.  

### Setup  your Spotify API credentials
To use any of the Spotify sources or sinks you'll need to get a Spotify API key. See this [documentation](http://spotipy.readthedocs.org/en/latest/#authorized-requests) in the Spotipy docs on how to get a key and how to set the credentials.

### Setup your Echo Nest API credentials
To use any of the Echo Nest sources or filters you'll need to get an Echo Nest API key:

  * Get an API key - to use the Echo Nest API you need an Echo Nest API key. You can get one for free at [developer.echonest.com](http://developer.echonest.com).
  * Set the API key - you can do this one of two ways:
Set an environment variable named ECHO\_NEST\_API\_KEY to your API key

## More Examples
A full set of examples can be found in the [online
documentation](http://pbl.readthedocs.org/) and in the [PBL examples
directory](https://github.com/plamere/pbl/tree/master/examples).
        

## Reporting Issues
If you have suggestions, bugs or other issues specific to this library, file them [here](https://github.com/plamere/pbl/issues). Or just send me a pull request.

## Version

- 1.0 - 06/20/2015 - Initial release
- 1.1.3 - 07/24/2015 - improved error handling, plus some new components
