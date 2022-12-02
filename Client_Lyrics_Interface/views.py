
from multiprocessing import context
from bs4 import BeautifulSoup
from django.shortcuts import HttpResponseRedirect, render
from django.contrib import messages
import time
from django import forms
from lyricsgenius import Genius
import requests
from .MarkovChain import *
from django.views.decorators.csrf import csrf_exempt
import json


lyrics = []

# make songs global so that it can be accessed by the other functions.
songs = []


def reset_songs():
    global songs
    songs = []


genius = Genius(
    'I9ceP8lra9tVkTCtlop-CiQojVy9_HhPpP2ZdnD_wEHcgphiDGVGm_a6MYRPHXto')

genius.verbose = True
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

song, album, artist = 0, 0, 0
song_names, album_names, artist_names = '', '', ''
number, length = 0, 0
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
        label='Number of lines in each song', min_value=10, max_value=20, initial=15)


def testing(request):
    return render(request, 'testing.html', {})


@csrf_exempt
def default_selection(request):
    return render(request, 'testing.html', {'form': None, 'messages': None, "songs": None})


@ csrf_exempt
def get_songs_fields(request):
    try:
        if request.method == 'POST':
            # Resest the songs http response to none.
            genius.timeout = 8
            artist_names, lyr, song_names = '', '', ''
            form = Song_Name_Form(request.POST)
            s = Selection_Box(request.POST)
            # select = Selection_Box(request.GET)
            song = request.POST['song_name']
            name = request.POST['artist_name']
            number = request.POST['number']
            length = request.POST['length']
            if form.is_valid():
                reset_songs()

                song = genius.search_song(song, name)
                song_names += song.title + '\n'
                lyr += song.lyrics

                generator = MarkovChain(corpus=' '.join([lyr]))
                for _ in range(int(number)):
                    gen = generator.gen_song(
                        lines=int(length), length_range=[7, 10])
                    gen = gen.splitlines()
                    song = []
                    for line in gen:
                        song.append(line)
                    songs.append(song)

                return HttpResponseRedirect('/')
        else:
            form = Song_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [1]
    except:
        print(RuntimeError("Something bad happened while generating lyrics..."))
    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": songs})


@csrf_exempt
def get_albums_fields(request):
    try:
        if request.method == 'POST':
            genius.timeout = 8
            artist_names, lyr = '', ''
            form = Album_Name_Form(request.POST)
            s = Selection_Box(request.POST)
            name = request.POST['artist_name']
            album_name = request.POST['album_name']
            if form.is_valid():

                # messages.info(request, str(request))
                # print(album + " by " + name)

                album = genius.search_album(name=album_name, artist=name)
                print(album)
                for song in album.tracks:
                    lyr += song.to_text()
                print(lyr[0])

                # s = genius.search_all("Drake")
                # song_id = s["sections"][0]['hits'][0]['result']['id']
                # print(song_id)
                # sons = genius.artist_songs(song_id,
                #                           sort='popularity',
                #                           per_page=1)
#
                #song_ids = []
                # for song in sons["songs"]:
                #    page = requests.get("https://genius.com" + song["path"])
                #    html = BeautifulSoup(page.text, "html.parser")
                #    [h.extract() for h in html('script')]
                #    l = html.find("div",
                #                  {"data-lyrics-container": "true"}).get_text(separator="\n")
                #    cleaned = re.sub(r'\[(.|\n)*?\]', ' ', l)
                #    cleaned = re.sub(r'\((.|\n)*?\)', ' ', cleaned)
                #    print(cleaned)
                # song_ids.append(song["id"])

                # l = []
                # for id in song_ids:

                # temp_lyrics = genius.lyrics(
                #    id, remove_section_headers=True)
                # song.join(temp_lyrics)
                # print(temp_lyrics)
                # l.append(temp_lyrics)

                #dd = ""
                # for d in l:
                #    dd += d

                # print(dd)
                # for hits in s["hits"]:
                #   for results in hits["result"]:
                # for title in results["full_title"]:
                #    print(title)
                #      for vals in results.title():
                #         print(vals)

                # for song in s:
                #    if s['title'] == "Rap God":
                #        song_id = s['id']
                # song = genius.song(song_id)
                # print(song)

                generator = MarkovChain(corpus=lyr)
                gen = generator.gen_song(
                    lines=15, length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    songs.append(line)

                return HttpResponseRedirect('/')
        else:

            form = Album_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [2]
    except:
        print(RuntimeError("Something bad happened while generating lyrics..."))
    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": songs})


@csrf_exempt
def get_artists_fields(request):
    try:
        if request.method == 'POST':
            genius.timeout = 8
            artist_names, lyr = '', ''
            form = Artist_Name_Form(request.POST)
            s = Selection_Box(request.POST)
            name = request.POST['artist_name']
            if form.is_valid():
                artist = genius.search_artist(
                    artist_name=name, max_songs=5)
                artist_names += artist.name + '\n'
                for song in artist.songs:
                    lyr += song.lyrics
                generator = MarkovChain(corpus=' '.join([lyr]))
                gen = generator.gen_song(
                    lines=15, length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    songs.append(line)
                return HttpResponseRedirect('/')
        else:
            form = Artist_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [3]
    except:
        print(RuntimeError("Something bad happened while generating lyrics..."))

    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": songs})
