
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


lyrics = []
songs = {}
credit = "..."

genius = Genius(
    'I9ceP8lra9tVkTCtlop-CiQojVy9_HhPpP2ZdnD_wEHcgphiDGVGm_a6MYRPHXto')


genius.verbose = True
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

song, album, artist = 0, 0, 0
song_names, album_names, artist_names = '', '', ''
corpus_lyrics = []
lyr = ''


def Placeholder_Text(text):
    return forms.TextInput(attrs={f'placeholder': text})


class Song_Name_Form(forms.Form):
    song_name = forms.CharField(
        label='Song', max_length=100, widget=Placeholder_Text('Enter any song'))
    artist_name = forms.CharField(
        label='Artist', max_length=100, widget=Placeholder_Text('Enter the artist'))
    # initial="twenty one pilots" is another option.


class Album_Name_Form(forms.Form):
    album_name = forms.CharField(
        label='Album', max_length=100, widget=Placeholder_Text('Enter any album'))
    artist_name = forms.CharField(
        label='Artist', max_length=100, widget=Placeholder_Text('Enter the artist'))


class Artist_Name_Form(forms.Form):
    # options = (('By_Artist', 'Generate from artist'))
    artist_name = forms.CharField(
        label='Artist', max_length=100, widget=Placeholder_Text('Enter any artist'))


class Selection_Box(forms.Form):
    selector = forms.ChoiceField(choices=(
        ("1", "Song(s)"),
        ("2", "Album(s)"),
        ("3", "Artist(s)")
    ), label='Generate a song based off...',
        widget=forms.RadioSelect,
        initial="1",
    )

    # Create a number select box to enter number 1-5 for the number of songs to generate
    # Give a label saying "hit generate to generate a song based off of the above selection"
    number = forms.IntegerField(
        label='Number of songs to generate', min_value=1, max_value=10, initial=1)
    length = forms.IntegerField(
        label='Number of lines in each song', min_value=1, max_value=30, initial=15)


def testing(request):
    return render(request, 'testing.html', {})


@csrf_exempt
def default_selection(request):
    return render(request, 'testing.html', {'form': None, 'messages': None, "songs": None})


@ csrf_exempt
def get_songs_fields(request):
    try:
        if not "generated_songs" in request.session:
            request.session["generated_songs"] = ["No Song to show..."]
        if request.method == 'POST':
            genius.timeout = 8
            artist_names, lyr, song_names = '', '', ''
            form = Song_Name_Form(request.POST)
            s = Selection_Box(request.POST)
            song = request.POST['song_name']
            name = request.POST['artist_name']
            choice = request.POST['selector']
            length = request.POST['length']
            if form.is_valid():
                song = genius.search_song(song, name)
                song_names += song.title + '\n'
                lyr = song.lyrics
                answer = []
                generator = MarkovChain(corpus=lyr)
                gen = generator.gen_song(lines= int(length), length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    answer.append(line)


                request.session['generated_songs'] = songs
                if name not in songs:
                    temp = []
                    temp.append(answer)
                    songs[name] = temp
                else:
                    temp = songs[name]
                    temp.append(answer )
                    songs[name] = temp
                
                return HttpResponseRedirect('/songs')
        else:
            form = Song_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [1]
    except Exception as e:
        print(RuntimeError("Something bad happened while generating lyrics..."))
        print(e)
    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": request.session['generated_songs']})


@csrf_exempt
def get_albums_fields(request):
    try:
        if not "generated_songs" in request.session:
            request.session["generated_songs"] = ["No Song to show..."]
        if request.method == 'POST':
            
            genius.timeout = 60
            artist_names, lyr, credit = '', '', '' 
            form = Album_Name_Form(request.POST)
            selections = Selection_Box(request.POST)
            name = request.POST['artist_name']
            album_name = request.POST['album_name']
            length = request.POST['length']
            
            if form.is_valid():
                album = genius.search_album(name=album_name, artist=name)
                for song in album.tracks:
                    lyr += song.to_text()
            
                answer = []
                generator = MarkovChain(corpus=lyr)
                gen = generator.gen_song(lines= int(length), length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    answer.append(line)

                request.session['generated_songs'] = songs
                if name not in songs:
                    temp = []
                    temp.append(answer)
                    songs[name] = temp
                else:
                    temp = songs[name]
                    temp.append(answer )
                    songs[name] = temp
                return HttpResponseRedirect('/albums')
        else:
            form = Album_Name_Form()
            selections = Selection_Box()
            selections.fields["selector"].initial = [2]
    except Exception as e:
        print(RuntimeError("Something bad happened while generating lyrics..."))
        print(e)

    return render(request, 'testing.html', {'form': form, 'select': selections, "songs": request.session["generated_songs"]})


@csrf_exempt
def get_artists_fields(request):
    try:
        if not "generated_songs" in request.session:
            request.session["generated_songs"] = ["No Song to show..."]
        if request.method == 'POST':
            genius.timeout = 8
            artist_names, lyr = '', ''
            form = Artist_Name_Form(request.POST)
            s = Selection_Box(request.POST)
            name = request.POST['artist_name']
            length = request.POST['length']
            song_number = request.POST['number']
            
            if form.is_valid():
                artist = genius.search_artist(
                    artist_name=name, max_songs=int(song_number))

                for song in artist.songs:
                    lyr += song.lyrics

                answer = []
                generator = MarkovChain(corpus=lyr)
                gen = generator.gen_song(lines= int(length), length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    answer.append(line)

                print(answer)
                request.session['generated_songs'] = songs
                if name not in songs:
                    temp = []
                    temp.append(answer)
                    songs[name] = temp
                else:
                    temp = songs[name]
                    temp.append(answer)
                    songs[name] = temp
                
                return HttpResponseRedirect('/artists')
        else:
            form = Artist_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [3]
    except Exception as e:
        print(RuntimeError("Something bad happened while generating lyrics..."))
        print(e)
        traceback.print_exc()

    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": request.session["generated_songs"]})
