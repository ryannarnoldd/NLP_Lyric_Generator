
from multiprocessing import context
from django.shortcuts import HttpResponseRedirect, render
from django.contrib import messages
import time
from django import forms
from lyricsgenius import Genius
from .MarkovChain import *
from django.views.decorators.csrf import csrf_exempt


lyrics = []
songs = []

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


class Artist_Name_Form(forms.Form):
    # options = (('By_Artist', 'Generate from artist'))
    artist_name = forms.CharField(
        label='Enter artist\'s name:', max_length=100)


class Album_Name_Form(forms.Form):
    artist_name = forms.CharField(
        label='Enter artist\'s name ', max_length=100)
    album_name = forms.CharField(
        label='Enter album by artist ', max_length=100)


class Song_Name_Form(forms.Form):
    artist_name = forms.CharField(
        label='Enter artist\'s name ', max_length=100)
    song_name = forms.CharField(
        label='Enter song name ', max_length=100)


class Selection_Box(forms.Form):
    selector = forms.ChoiceField(choices=(
        ("1", "Generate a song based off an artist"),
        ("2", "Generate a song based on an album by an artist"),
        ("3", "Generate a song based on artist and their albums")
    ),
        widget=forms.RadioSelect,
        initial="1"
    )


def testing(request):
    return render(request, 'testing.html', {})


@csrf_exempt
def default_selection(request):
    return render(request, 'testing.html', {'form': None, 'messages': None, "songs": None})


@csrf_exempt
def get_name_fields(request):
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
            s.fields["selector"].initial = [1]
    except:
        print(RuntimeError("Something bad happened while generating lyrics..."))

    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": songs})


@csrf_exempt
def get_album_fields(request):
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
                #print(album + " by " + name)
                album = genius.search_album(name=album_name, artist=name)
                print(album)
                for song in album.tracks:
                    lyr += song.to_text()

                generator = MarkovChain(corpus=' '.join([lyr]))
                gen = generator.gen_song(
                    lines=15, length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    songs.append(line)

            return HttpResponseRedirect('/album')
        else:

            form = Album_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [2]
    except Exception as e:
        #print(RuntimeError("Something bad happened while generating lyrics..."))
        print(e)

    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": songs})


@csrf_exempt
def get_song_fields(request):
    try:
        if request.method == 'POST':
            genius.timeout = 8
            artist_names, lyr = '', ''
            form = Song_Name_Form(request.POST)
            s = Selection_Box(request.POST)
            # select = Selection_Box(request.GET)
            song = request.POST['song_name']
            name = request.POST['artist_name']
            choice = request.POST['selector']
            if form.is_valid():

                # messages.info(request, str(request))
                song = genius.search_song(song + " by " + name)

                song_names += song.full_title + '\n'
                lyr += song.lyrics

                generator = MarkovChain(corpus=' '.join([lyr]))
                gen = generator.gen_song(
                    lines=15, length_range=[7, 10])
                gen = gen.splitlines()
                for line in gen:
                    songs.append(line)
                # gen = "fThese lyrics were inspired by... \n" +  + '\n\n'
                return HttpResponseRedirect('/')
        else:
            form = Song_Name_Form()
            s = Selection_Box()
            s.fields["selector"].initial = [3]
    except:
        print(RuntimeError("Something bad happened while generating lyrics..."))
    return render(request, 'testing.html', {'form': form, 'select': s, 'messages': lyrics, "songs": songs})
