from django.urls import path
from Client_Lyrics_Interface import views

urlpatterns = [
    path('', views.get_songs, name='Main')
    #path('form/', views.get_name, name="get_name")
]
