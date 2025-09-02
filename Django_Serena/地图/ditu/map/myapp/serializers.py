# myapp/serializers.py

from rest_framework import serializers
from .models import Location, Article

class LocationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    image = serializers.ImageField(required=False)
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'description', 'image', 'owner']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'pub_date']