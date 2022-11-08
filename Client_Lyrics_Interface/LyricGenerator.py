import asyncio
from lyricsgenius import Genius
import csv
import json
from .MarkovChain import *
import re

import threading
import time

genius = Genius(
    'I9ceP8lra9tVkTCtlop-CiQojVy9_HhPpP2ZdnD_wEHcgphiDGVGm_a6MYRPHXto')

genius.verbose = False
genius.remove_section_headers = True
genius.skip_non_songs = False
genius.excluded_terms = ["(Remix)", "(Live)"]

song, album, artist = 0, 0, 0
song_names, album_names, artist_names = '', '', ''
corpus_lyrics = []
lyr = ''


def get_song(n):
    print(f"HELLO THREAD {n}")
    s = genius.search_song("the motto", "Drake")

    # await asyncio.sleep(time.sleep(20))


def repl():
    print('\n1. Add a song.\n2. Add an album.\n3. Add an artist.\n0. Generate lyrics.')
    action = int(input('Choose an action: '))
    while action != 0:
        match action:
            case 1:
                song = genius.search_song(
                    *input('\nEnter a song: ').split(' by '))
                song_names += song.full_title + '\n'
                lyr += song.lyrics

            case 2:
                album = genius.search_album(input('\nEnter an album: '))
                album_names += album.name + ' by ' + album.artist.name + '\n'

                for song in album.tracks:
                    lyr += song.to_text()
                # corpus_lyrics.append(album.to_text())
            case 3:
                artist = genius.search_artist(
                    input('\nEnter an artist: '), max_songs=5)
                artist_names += artist.name + '\n'
                for song in artist.songs:
                    lyr += song.lyrics
                    # corpus_lyrics.append(song.lyrics)

        print('\n1. Add a song.\n2. Add an album.\n3. Add an artist.\n0. Generate lyrics.')
        action = int(input('Choose an action: '))

    # not using corpus_lyrics right now.
    generator = MarkovChain(corpus=' '.join([lyr]))
    gen = generator.gen_song(lines=15, length_range=[7, 10])
    gen = gen.splitlines()

    print('\n')
    if song_names:
        print(f'Song(s):\n{song_names}')
    if album_names:
        print(f'Album(s):\n{album_names}')
    if artist_names:
        print(f'Artist(s):\n{artist_names}')
    for line in gen:
        print(line)
    print()

    #   WRITING TO CSV FILES.
    # fields = ['Album', 'Song_title', 'Year', 'Lyrics']
    # filename = "lyrics.csv"
    # with open(filename, 'w') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     for song in artist.songs:
    #         lyrics_list = []
    #         lyrics_list.append(song.lyrics)
    #         print(song.to_json())
    #         album = song.album.name
    #         title = song.title
    #         year = song.year
    #         lyrics = song.lyrics
    #         csvwriter.writerow([album,title,year,lyrics])
    #

    #   WRITING JSON.
    # lyricsf = genius.search_album("SOUR").to_text()
    # with open("song.json", "w") as outfile:
    #     json.dump(lyricsf, outfile)
