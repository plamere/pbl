.. pbl documentation master file, created by
   sphinx-quickstart on Sat Jun 20 07:20:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: images/spotify-web-api-doc.jpg
   :width: 100 %

The Playlist Builder Library
=============================

The Playlist Builder Library (PBL) is a Python library that you can use to
create playlists. 

A Quick Example
---------------
For example, let's say you like to listen to music on your morning commute. You
mostly like to listen to classic rock, but you don't want to get too out of
touch with new music so you'd like a little bit of new music thrown in as well.
With PBL you can easily create a such a playlist like so::

    from pbl import *

    classic_rock = Sample(PlaylistSource('Rock Classics'), sample_size=10)
    new_music = Sample(PlaylistSource('New Music Tuesday'), sample_size=5)
    combined = Shuffler(Concatenate([classic_rock, new_music]))
    show_source(combined)

This program grabs the 'Rock Classics' playlist from Spotify (by searching for
the most popular playlist on Spotify with that name), and randomly samples 10
tracks from it. Similarly it randomly samples 5 tracks from the 'New Music
Tuesday' playlist. It concatentates these two playlists together and shuffles
them. Here's the resulting output::

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

As you can see, that's 15 songs, 5 are new, and 10 are classic.
The function **show_source** shows the playlist in the terminal, but of course
to listen to a playlist, it needs to be saved on Spotify. We can do that by
adding a PlaylistSave call like so::

    from pbl import *

    classic_rock = Sample(PlaylistSource('Rock Classics'), sample_size=10)
    new_music = Sample(PlaylistSource('New Music Tuesday'), sample_size=5)
    combined = Shuffler(Concatenate([classic_rock, new_music]))
    combined = PlaylistSave(combined, 'my morning commute', 'plamere')
    show_source(combined)

Now, whenever the program is run, my 'my morning commute' playlist will be updated will be updated with a different set of tracks sampled from Rock Classics and New Music Tuesday.

Quick Start
-----------
To get started, install **pbl** with::

    % pip install pbl

this should take care of all the dependencies (including spotipy, pyen and others).

Once installed, just **import pbl** and you'll have everything you need.  Here
are a few more quick examples to give you a taste of the kind of things you can
do with **PBL**.

Setup  your Spotify API credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To use any of the Spotify sources or sinks you'll need to get a Spotify API key. See http://spotipy.readthedocs.org/en/latest/#authorized-requests in the Spotipy docs on how to get a key and how to set the credentials.

Setup your Echo Nest API credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To use any of the Echo Nest sources or filters you'll need to get an Echo Nest API key:

  * Get an API key - to use the Echo Nest API you need an Echo Nest API key. You can get one for free at http://developer.echonest.com.
  * Set an environment variable named ECHO\_NEST\_API\_KEY to your API key


More examples
----------------
Here are a few more examples to give you a feel for what you can do with **PBL**.

Playlist of 30 minutes of the lowest energy songs from Your Favorite Coffeehouse::

    import pbl

    coffeehouse = pbl.PlaylistSource('Your Favorite Coffeehouse')
    coffeehouse = pbl.Annotator(coffeehouse, 'echonest')
    coffeehouse = pbl.Sorter(coffeehouse, 'echonest.energy')
    coffeehouse = pbl.LongerThan(coffeehouse, 30 * 60)
    pbl.show_source(coffeehouse, props=['duration', 'echonest.energy'])

**Output**::

    1 Fortune - Acoustic -- William Fitzsimmons
        duration -> 228
        echonest.energy -> 0.055224
    2 I Know It’s Pathetic But That Was the Greatest Night of My Life -- Sun Kil Moon
        duration -> 107
        echonest.energy -> 0.061157
    3 I Shall Cross This River -- The Black Atlantic
        duration -> 201
        echonest.energy -> 0.100383
    4 Say Yes -- Elliott Smith
        duration -> 135
        echonest.energy -> 0.109814
    5 Hurricane -- Mindy Smith
        duration -> 212
        echonest.energy -> 0.110599
    6 I Knew This Would Be Love -- Imaginary Future
        duration -> 210
        echonest.energy -> 0.119146
    7 Emmeline -- Bruno Merz
        duration -> 250
        echonest.energy -> 0.124862
    8 A Heart Arcane -- Horse Feathers
        duration -> 169
        echonest.energy -> 0.12929
    9 Come Home -- Ryan Adams
        duration -> 290
        echonest.energy -> 0.132386

Sort by title length
~~~~~~~~~~~~~~~~~~~~
Re-sort the Teen Party Playlist in order of the length of the title and artist::

    from  pbl import *

    tp = CustomSorter(PlaylistSource('Teen Party'),
        lambda tid: len(tlib.get_attr(tid, 'title') + tlib.get_attr(tid, 'artist')))
    show_source(tp)

**Output**::

    1 Fun -- Pitbull
    2 Bad Girls -- MKTO
    3 21 -- Hunter Hayes
    4 Fancy -- Iggy Azalea
    5 Elastic Heart -- Sia
    6 Sparks -- Hilary Duff
    7 Beautiful Now -- Zedd
    8 Emergency -- Icona Pop
    9 In My Head -- Galantis
    10 Firework -- Katy Perry
    11 Back of the Car -- RAC
    12 Stitches -- Shawn Mendes
    13 Worth It -- Fifth Harmony
    14 Beat of My Drum -- Powers
    15 Black Magic -- Little Mix
    16 Sunshine -- Young Empires
    17 Waiting For Love -- Avicii
    18 Victoria -- Jordan Bratton
    19 Uma Thurman -- Fall Out Boy
    20 Love Me Badder -- Elliphant
    21 Pray to God -- Calvin Harris
    22 Good Thing -- Sage The Gemini
    23 Pity Party -- Melanie Martinez
    24 Pretty Girls -- Britney Spears
    25 Want To Want Me -- Jason Derulo
    26 One In A Million -- Hilary Duff
    27 Woke The F*ck Up -- Jon Bellion
    28 Another You -- Armin van Buuren
    29 Honey, I'm Good. -- Andy Grammer
    30 Can't Feel My Face -- The Weeknd
    31 You Know You Like It -- DJ Snake
    32 Together - Radio Edit -- CAZZETTE
    33 Ignition/Do You... -- Phoebe Ryan
    34 Shut Up and Dance -- Walk the Moon
    35 Drop Dead Beautiful -- Elijah Blake
    36 Around The World -- Natalie La Rose
    37 New York Raining -- Charles Hamilton
    38 Bitch Better Have My Money -- Rihanna
    39 Zero Gravity - Radio Edit -- Borgeous
    40 I Really Like You -- Carly Rae Jepsen
    41 The Night Is Still Young -- Nicki Minaj
    42 Flex (Ooh, Ooh, Ooh) -- Rich Homie Quan
    43 Senses (feat. Lostboycrow) -- Cheat Codes
    44 Lean On (feat. MØ & DJ Snake) -- Major Lazer
    45 Where Are Ü Now (with Justin Bieber) -- Jack Ü
    46 Cheerleader - Felix Jaehn Remix Radio Edit -- OMI
    47 Marvin Gaye (feat. Meghan Trainor) -- Charlie Puth
    48 Walk The Moon - Teen Party Intro -- Various Artists
    49 Powerful (feat. Ellie Goulding & Tarrus Riley) -- Major Lazer
    50 Hey Mama (feat. Nicki Minaj, Bebe Rexha & Afrojack) -- David Guetta


Dad's Selfish Playlist
~~~~~~~~~~~~~~~~~~~~~~
Dad is on a roadtrip with daughter. They agree to alternate between dad's music
and daughter's music. Dad is selfish, so he makes a playlist that alternates the
longest cool jazz tracks with the shortest teen party playlists with this
script::

    from pbl import *

    teen_party = First(Sorter(PlaylistSource('Teen Party'), 'duration'), 10)
    jazz_classics = Last(Sorter(PlaylistSource('Jazz Classics'), 'duration'), 10)
    both = Alternate([teen_party, Reverse(jazz_classics)])
    show_source(both, props=['duration', 'src'])


**Output**::

    1 Walk The Moon - Teen Party Intro -- Various Artists
        spotify.duration_ms -> 7500
        src -> Teen Party
    2 Feed The Fire -- Geri Allen
        spotify.duration_ms -> 683160
        src -> Jazz Classics
    3 Pretty Girls -- Britney Spears
        spotify.duration_ms -> 163960
        src -> Teen Party
    4 Turiya & Ramakrishna -- Alice Coltrane
        spotify.duration_ms -> 498146
        src -> Jazz Classics
    5 Emergency -- Icona Pop
        spotify.duration_ms -> 169617
        src -> Teen Party
    6 Real & Imagined -- Kait Dunton
        spotify.duration_ms -> 465573
        src -> Jazz Classics
    7 Lean On (feat. MØ & DJ Snake) -- Major Lazer
        spotify.duration_ms -> 176561
        src -> Teen Party
    8 Stand by me -- Buika
        spotify.duration_ms -> 442693
        src -> Jazz Classics
    9 Flex (Ooh, Ooh, Ooh) -- Rich Homie Quan
        spotify.duration_ms -> 177057
        src -> Teen Party
    10 Bewitched, Bothered, And Bewildered -- Ella Fitzgerald
        spotify.duration_ms -> 421466
        src -> Jazz Classics
    11 Cheerleader - Felix Jaehn Remix Radio Edit -- OMI
        spotify.duration_ms -> 180021
        src -> Teen Party
    12 Les Feuilles Mortes / Autumn Leaves -- Dee Dee Bridgewater
        spotify.duration_ms -> 409000
        src -> Jazz Classics
    13 Sparks -- Hilary Duff
        spotify.duration_ms -> 185946
        src -> Teen Party
    14 Falling In Love with Love -- Eliane Elias
        spotify.duration_ms -> 386493
        src -> Jazz Classics
    15 Marvin Gaye (feat. Meghan Trainor) -- Charlie Puth
        spotify.duration_ms -> 187741
        src -> Teen Party
    16 Violets For Your Furs - 2007 - Remaster -- Jutta Hipp
        spotify.duration_ms -> 369568
        src -> Jazz Classics
    17 Together - Radio Edit -- CAZZETTE
        spotify.duration_ms -> 188170
        src -> Teen Party
    18 I Didn't Know What Time It Was -- Cecile McLorin Salvant
        spotify.duration_ms -> 367493
        src -> Jazz Classics
    19 Another You -- Armin van Buuren
        spotify.duration_ms -> 192306
        src -> Teen Party
    20 J.P. Vanderbilt IV -- Charlie Shavers
        spotify.duration_ms -> 350600
        src -> Jazz Classics


The resulting playlist has is filled with long Jazz tracks (no shorter than 5
minutes) and short Teen Party tracks (no longer than 3 minutes).

Using PBL
===========
In PBL you create a pipeline of objects that contribute to the playlist.
Typically an object in the pipeline will pull tracks from upstream, process them
and make them available for objects that are downstream in the pipeline. The
pipeline contains at least one **Source** object and will typically include
**Operator** objects, **Filter** objects, **Sorting** objects and **Sink** objects. Read on to learn more about the different types of objects.

Sources
----------
These objects are the source of tracks in a pipeline

Spotify Sources
~~~~~~~~~~~~~~~~
  * **AlbumSource** - produces tracks from the given album
  * **ArtistTopTracks** - produces the top tracks for a given artist
  * **PlaylistSource** - poroduces tracks from a Spotify Playlist
  * **TrackSource** - produces the given tracks

Echo Nest Sources
~~~~~~~~~~~~~~~~~
  * **EchoNestArtistPlaylist** - produces tracks from the given artist
  * **EchoNestArtistRadio** - produces tracks from the given artist and similar artists
  * **EchoNestGenreRadio** - produces tracks from the given genre
  * **EchoNestHotttestSongs** - produces the most popular songs
  * **EchoNestPlaylist** - Uses the Echo Nest playlist API to generate a wide range of track sequences

Generic Sources
~~~~~~~~~~~~~~~
  * **FakeTrackSource** - produces an infinite supply of fake tracks


Operators
~~~~~~~~~
Operators work on a pipeline of tracks
  
  * **Alternate** - takes a list of multiple sources and produces a stream of tracks drawn from the sources
  * **Annotate** - Annotates tracks with data from a source such as Spotify or The Echo Nest
  * **Buffer** - Collects a fixed number of tracks (useful when a source could generate a large number of tracks)
  * **Case** - Conditionally choses tracks from multiple sources
  * **Concatentate** - concatenates streams
  * **Conditional** - choses between two streams based on a conditional function
  * **DeDup** - De-duplicates tracks from a stream
  * **First** - Returns the first N tracks from a stream
  * **Last** - Returns the last N tracks from a stream
  * **LongerThan** - Stops the stream when the track duration is longer than the given time
  * **Looper** - Loops through a stream forever
  * **Sample** - Randomly samples tracks from a stream
  * **ShorterThan** - Stops the stream when the next track would make the total stream duration longer than the given time
  * **Split** - Split a stream into two streams

Filters
~~~~~~~
  * **ArtistFilter** - Removes tracks from the stream that match the given aritsts
  * **AttributeRangeFilter** - Filter the stream to only include tracks where the given attribute is in the given range
  * **TrackFilter** - Filter the stream to include tracks that are NOT in the given filter playlist

Sorting
~~~~~~~
  * **CustomSorter** - sort the stream based upon a custom key
  * **Reverse** - reverse the order of the tracks in the stream
  * **Shuffler** - randomly shuffle the order of the tracks
  * **Sorter** - sort the tracks by an attribute

Sinks
~~~~~
  * **Debugger** - dump all details of each track in the stream
  * **Dumper** - show tracks with configurable properties in the stream
  * **PlaylistSave** - save the playlist to spotify
  * **SaveToJson** - save the playlist to a json file

  
API Reference
==============

:mod:`standard` Module
=======================
.. automodule:: pbl.standard_plugs
    :members:

:mod:`engine` Module
====================
.. automodule:: pbl.engine
    :members:

:mod:`spotify` Module
=====================
.. automodule:: pbl.spotify_plugs
    :members:

:mod:`echonest` Module
======================
.. automodule:: pbl.echonest_plugs
    :members:

:mod:`track_manager` Module
===========================
.. automodule:: pbl.track_manager
    :members:

:mod:`frog` Module
==================
.. automodule:: pbl.frog
    :members:

Frequently Asked Questions
==========================
 * **I get an spotipy.oauth2.SpotifyOauthError: No client id error, what do I do?**  You need to set up your Spotify API credentials. See the **Quick Start** section for more details.
 * **I get an error pyen.PyenConfigurationException: Can't find your API keyanywhere, what do I do?** You need to set up your Echo Nest API credentials.  See the **Quick Start** for more details. 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

