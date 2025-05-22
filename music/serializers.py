from rest_framework import serializers
from .models import Song, Like

class SongSerializer(serializers.ModelSerializer):
    liked = serializers.BooleanField(read_only=True)
    class Meta:
        model = Song
        fields = "__all__"

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"