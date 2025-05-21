from django.db import models
from authentication.models import CustomUser
from django.db.models import QuerySet
from django.db.models import Count, Q, Subquery, OuterRef

# Create your models here.

class Song(models.Model):
    title = models.CharField(max_length=256)
    artist_name = models.CharField(max_length=256)
    audio_file = models.FileField(upload_to='songs/')
    image = models.ImageField(upload_to="song_images", default=None, null=True)
    genre = models.CharField(max_length=128)

    @staticmethod
    def get_liked_by_user(user: CustomUser)-> QuerySet:
        return Song.objects.filter(like__user=user)

    @staticmethod
    def get_recommended_for_user(user: CustomUser)-> QuerySet:
        liked_genres = Song.objects.filter(like__user=user).values_list('genre', flat=True).distinct()
        recommendation = Song.objects\
            .exclude(like__user=user)\
            .filter(genre__in=liked_genres)\
            .annotate(genre_likes=Count('like'))\
            .order_by('-genre_likes')
        return recommendation

    @staticmethod
    def search(query: str)-> QuerySet:
        query_words = query.split()
        q_objects = Q()
        for word in query_words:
            q_objects |= Q(title__icontains=word)
            q_objects |= Q(artist_name__icontains=word)
        similar_songs = Song.objects.filter(q_objects).distinct()
        return similar_songs


    def __str__(self):
        return f"{self.title}"


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ("user", "song")
        ]

    def __str__(self):
        return f"{self.user}, {self.song}"