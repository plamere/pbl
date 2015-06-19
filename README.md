# The Playlist Builder Libarary

The Playlist Builder Library (PBL) is a Python library that you can use to
create playlists. 

## A Quick Example
For example, let's say you like to listen to music on your morning commute. You
mostly like to listen to classic rock, but you don't want to get too out of
touch with new music so you'd like a little bit of new music thrown in as well.
With PBL you can easily create a such a playlist like so:

```python 
from pbl import *

classic_rock = Sample(PlaylistSource('Rock Classics'), sample_size=10)
new_music = Sample(PlaylistSource('New Music Tuesday'), sample_size=5)
combined = Shuffler(Concatenate([classic_rock, new_music]))
show_source(combined)
```

This program grabs the 'Rock Classics' playlist from Spotify (by searching for
the most popular playlist on Spotify with that name), and randomly samples 10
tracks from it. Similarly it randomly samples 5 tracks from the 'New Music
Tuesday' playlist. It concatentates these two playlists together and shuffles
them. Here's the resulting output:

```
    1 Livin On A Prayer -- Bon Jovi
    2 She Used to Love Me a Lot -- Johnny Cash
    3 face the sun -- Miguel
    4 Get Paid -- Vince Staples
    5 1992 -- AIR BAG ONE
    6 Black Betty -- Ram Jam
    7 Vince Staples - New Music Tuesday Intro -- Various Artists
    8 Give Me Something -- Jarryd James
    9 Don't Stop Believin' -- Journey
    10 Hush - 1998 Remastered Version -- Deep Purple
    11 Freak on a Leash -- Korn
    12 Best Of You -- Foo Fighters
    13 Paint It, Black -- The Rolling Stones
    14 The Final Countdown -- Europe
```

As you can see, that's 15 songs, 5 are new, and 10 are classic.

