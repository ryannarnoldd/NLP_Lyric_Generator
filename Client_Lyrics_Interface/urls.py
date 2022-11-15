from django.urls import path
from Client_Lyrics_Interface import views

urlpatterns = [
    path('', views.get_song_fields, name='testing'),
    path('songs', views.get_song_fields, name='testing'),
    path('album', views.get_album_fields, name='testing'),
    path('artists', views.get_artist_fields, name='testing'),
    #path('form/', views.get_name, name="get_name")
]
