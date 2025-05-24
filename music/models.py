from django.db import models
from django.db.models import Exists, OuterRef
from authentication.models import CustomUser
from django.db.models import QuerySet
from django.db.models import Count, Q, Subquery, OuterRef
from django.db.models import Count, OuterRef, Subquery, IntegerField, Q

# Create your models here.

class Song(models.Model):
    title = models.CharField(max_length=256)
    artist_name = models.CharField(max_length=256)
    audio_file = models.FileField(upload_to='songs/')
    image = models.ImageField(upload_to="song_images", default=None, null=True)
    genre = models.CharField(max_length=128)

    @staticmethod
    def annotate_by_like(user: CustomUser, queryset: QuerySet=None)-> QuerySet:
        if not queryset:
            queryset = Song.objects.all()
        liked_subquery = Like.objects.filter(user=user, song=OuterRef('pk'))
        annotated_by_like = queryset.annotate(liked=Exists(liked_subquery))
        return annotated_by_like



    @staticmethod
    def get_liked_by_user(user: CustomUser)-> QuerySet:
        return Song.annotate_by_like(user).filter(like__user=user)

    @staticmethod
    def get_recommended_for_user(user: CustomUser)-> QuerySet:

        # Step 1: Get genres the user has liked
        liked_genres = Song.objects.filter(like__user=user).values('genre').distinct()
        # Step 2: Subquery to count likes per genre
        genre_like_counts = Like.objects.filter(song__genre=OuterRef('genre'))\
            .values('song__genre')\
            .annotate(genre_likes=Count('id'))\
            .values('genre_likes')
        # Step 3: Filter songs not liked by the user, with liked genres, and annotate
        recommendation = Song.objects.filter(
            genre__in=Subquery(liked_genres.values('genre'))).exclude(
            like__user=user
        ).annotate(genre_likes=Subquery(genre_like_counts, output_field=IntegerField()))\
        .order_by('-genre_likes', '-id')  # sort by genre like count (ascending), then id as tie-breaker
        return recommendation

    @staticmethod
    def search(user: CustomUser, query: str)-> QuerySet:
        query_words = query.split()
        q_objects = Q()
        for word in query_words:
            q_objects |= Q(title__icontains=word)
            q_objects |= Q(artist_name__icontains=word)
        similar_songs = Song.annotate_by_like(user).filter(q_objects).distinct()
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