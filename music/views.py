from rest_framework import views, generics
from .models import Song, Like
from .serializers import SongSerializer
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

class SongListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SongSerializer

    def get_queryset(self):
        return Song.annotate_by_like(self.request.user)

class LikedListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SongSerializer

    def get_queryset(self):
        user = self.request.user
        return Song.get_liked_by_user(user)

class RecommendSongListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SongSerializer

    def get_queryset(self):
        user = self.request.user
        recommendation = Song.get_recommended_for_user(user)
        return recommendation

class SearchSongListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SongSerializer

    def get_queryset(self):
        request: Request = self.request
        user = self.request.user
        query = request.GET.get('q', '').strip()
        search_result = Song.search(user, query)
        return search_result

class LikeSongAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)

        like, created = Like.objects.get_or_create(
            user=request.user,
            song=song,
            defaults={'user': request.user, 'song': song}
        )

        if created:
            return Response(
                {"message": "Song liked successfully."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "You already liked this song."},
                status=status.HTTP_200_OK
            )

class UnlikeSongAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        like = Like.objects.filter(user=request.user, song=song).first()

        if like:
            like.delete()
            return Response(
                {"message": "Song unliked successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "You haven't liked this song."},
                status=status.HTTP_200_OK
            )