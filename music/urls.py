from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.SongListAPIView.as_view()),
    path("like/<int:song_id>/", views.LikeSongAPIView.as_view()),
    path("unlike/<int:song_id>/", views.UnlikeSongAPIView.as_view()),
    path("liked/", views.LikedListAPIView.as_view()),
    path("recommend/", views.RecommendSongListAPIView.as_view()),
    path("search/", views.SearchSongListAPIView.as_view())
]