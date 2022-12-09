
from multiprocessing import context
import re
from collections import defaultdict
import random
from bs4 import BeautifulSoup
from django.shortcuts import HttpResponseRedirect, render
from django.contrib import messages
import time
from django import forms
from lyricsgenius import Genius
import requests
from django.views.decorators.csrf import csrf_exempt
import json
import traceback
from dotenv import load_dotenv
import os
from django.core.validators import RegexValidator

class MarkovChain:
    def __init__(self, corpus='', starting_words='', order=2, length=8):
        self.order = order
        self.length = length
        self.words = re.findall("[a-z]+[']*[a-z]+", corpus.lower())
        self.starting_words = starting_words
        self.states = defaultdict(list)

        for i in range(len(self.words) - self.order):
            self.states[tuple(self.words[i:i + self.order])
                        ].append(self.words[i + self.order])

    def gen_sentence(self, length=8, startswith=None):
        terms = None
        if startswith:
            start_seed = [x for x in self.states.keys() if startswith in x]
            if start_seed:
                terms = list(start_seed[0])
        if terms is None:
            start_seed = random.randint(0, len(self.words) - self.order)
            terms = self.words[start_seed:start_seed + self.order]

        for _ in range(length):
            terms.append(random.choice(
                self.states[tuple(terms[-self.order:])]))

        return ' '.join(terms)

    def gen_song(self, lines=10, length=8, length_range=None):
        song = []
        if self.starting_words:
            song.append(self.gen_sentence(
                length=length, startswith=self.starting_words))
            lines -= 1
        for _ in range(lines):
            sent_len = random.randint(
                *length_range) if length_range else length
            song.append(self.gen_sentence(length=sent_len))

        return '\n'.join(song)

load_dotenv()
genius_token = os.getenv('GENIUS_TOKEN')
genius = Genius(genius_token)

genius.verbose = True
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]
# genius.sleep_time = 2
genius.retries = 1
genius.timeout = 8

song, album, artist = None, None, None
song_names, album_names, artist_names = '', '', ''
lyrics = ''

class Settings_Box(forms.Form):
    number = forms.IntegerField(
        label='Number of songs to generate', min_value=1, max_value=10, initial=1)
    length = forms.IntegerField(
        label='Number of lines in each song', min_value=1, max_value=30, initial=15)
    creativity = forms.IntegerField(
        label='Creativity',
        widget=forms.NumberInput(attrs={'type':'range', 'step': '4', 'min': '0', 'max': '100', 'initial': '100'}))

class All_Form(forms.Form):
    songs_input = forms.CharField(
        label = '',
        initial= "stressed out - twenty one pilots\ndrivers license - Olivia Rodrigo\ncardigan - Taylor Swift",
        required=False,
        validators=[RegexValidator('(?m:(^[a-zA-Z0-9 ]* - [a-zA-Z0-9 ]*$\r?\n?)+)', 'Please follow correct input format.')],
        widget=forms.Textarea(
            attrs={"rows":"10", "cols":"5", "placeholder": "Enter song(s) (one per line)", 
            "style": "width: 33.333333%; float:left; resize: none"}))

    albums_input = forms.CharField(
        label = '',
        initial = "SOUR - Olivia Rodrigo\nFolklore - Taylor Swift\nTrench - twenty one pilots",
        required=False,
        validators=[RegexValidator('(?m:(^[a-zA-Z0-9 ]* - [a-zA-Z0-9 ]*$\r?\n?)+)', 'Please follow correct input format.')],
        widget=forms.Textarea(
            attrs={"rows":"10", "cols":"5", "placeholder": "Enter album(s) (one per line)", 
            "style": "width: 33.333333%; float:left; resize: none"}))

    artists_input = forms.CharField(
        label = '',
        initial = "Taylor Swift\nPanic! at the Disco\ntwenty one pilots",
        required=False,
        validators=[RegexValidator('(?m:(^[a-zA-Z0-9 ]*$\r?\n?)+)', 'Please follow correct input format.')],
        widget=forms.Textarea(
            attrs={"rows":"10", "cols":"5", "placeholder": "Enter artist(s) (one per line)", 
            "style": "width: 33.333333%; float:left; resize: none;"}))

@csrf_exempt
def default_selection(request):
    return render(request, 'testing.html', {'form': None, 'settings': None, 'message': None, "songs": None})

@csrf_exempt
def get_songs(request):
    try:
        if request.method == 'POST':
            lyrics = ''
            inspired_songs, inspired_albums, inspired_artists = [], [], []
            form = All_Form(request.POST)
            settings = Settings_Box(request.POST)

            songs_input = request.POST['songs_input'].splitlines()
            songs_input = [tuple(song.split(" - ")) for song in songs_input if song != '']

            albums_input = request.POST['albums_input'].splitlines()
            albums_input = [tuple(album.split(" - ")) for album in albums_input if album != '']

            artists_input = request.POST['artists_input'].splitlines()
            artists_input = [artist for artist in artists_input if artist != '']

            length = int(request.POST['length'])
            song_number = int(request.POST['number'])
            creativity = 50 * round(int(request.POST['creativity'])/50)
            creativity = 4 - int(int(creativity)/50)
            
            if form.is_valid() and settings.is_valid():
                if songs_input == [] and albums_input == [] and artists_input == []:
                    return render(request, 'testing.html', {'form': form, 'settings': settings, 'message': 'Please enter at least one song, album, or artist.', "songs": None})
                
                for song_name in songs_input:
                    song = genius.search_song(*song_name)
                    if song == None:
                        return render(request, 'testing.html', {'form': form, 'settings': settings, 'message': f'{" - ".join(song_name)} is not a VALID song.', "songs": None})
                    inspired_songs.append(song.full_title.strip())
                    lyrics += song.lyrics
                
                for album_name in albums_input:
                    album = genius.search_album(*album_name)
                    if album == None:
                        return render(request, 'testing.html', {'form': form, 'settings': settings, 'message': f'{" - ".join(list(album))} is not a VALID album.', "songs": None})
                    inspired_albums.append(album.full_title.strip())
                    lyrics += album.to_text()

                for artist_name in artists_input:
                    artist = genius.search_artist(artist_name, max_songs=1)
                    if artist == None:
                        return render(request, 'testing.html', {'form': form, 'settings': settings, 'message': f'{artist_name} is not a VALID artist.', "songs": None})
                    inspired_artists.append(artist.name.strip())
                    for song in artist.songs:
                        lyrics += song.lyrics

                generator = MarkovChain(corpus=lyrics, order=creativity)
                song_list = []
                for _ in range(song_number):
                    gen = generator.gen_song(lines= int(length), length_range=[7, 10])
                    song_list.append(gen.splitlines())

                request.session['generated_songs'] = {
                    "inspired": {
                        "songs": inspired_songs,
                        "albums": inspired_albums,
                        "artists": inspired_artists,
                    },
                    "lyrics": [
                        song_list
                    ]
                }

            # Regex validation failed.
            else:
                settings = Settings_Box()
                form = All_Form()
                return render(request, 'testing.html', {'form': form, 'settings': settings, 'message': "Please follow correct input format.", "songs": None})
        
        # GET request.
        else:
            settings = Settings_Box()
            form = All_Form()
            request.session['generated_songs'] = None # Reset session.
        
    # Something bad happened.
    except Exception as e:
        print(e)
        traceback.print_exc()
        return render(request, 'testing.html', {'form': form, 'settings': settings, 'message': "Something bad happened while generating lyrics...", "songs": None})
        
    # Everything went well.
    return render(request, 'testing.html', {'form': form, 'settings': settings, "message": None, "songs": request.session["generated_songs"]})