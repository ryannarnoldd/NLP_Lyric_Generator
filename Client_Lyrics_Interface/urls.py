from django.urls import path
from Client_Lyrics_Interface import views

urlpatterns = [
    path('', views.get_songs_fields, name='testing'),
    path('songs', views.get_songs_fields, name='testing'),
    path('albums', views.get_albums_fields, name='testing'),
    path('artists', views.get_artists_fields, name='testing'),
    #path('form/', views.get_name, name="get_name")
]
