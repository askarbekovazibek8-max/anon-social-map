from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import AnonUser, AnonymousPost, Tag, FriendRelation, UserLocation, LocationShare

class PublicUserSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    class Meta:
        model = AnonUser; fields = ('anon_code', 'pseudonym', 'posts_count')
    def get_posts_count(self, obj): return obj.posts.count()

class TagSerializer(serializers.ModelSerializer):
    class Meta: model = Tag; fields = ('id', 'name')
class PostSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True); tags = TagSerializer(many=True, read_only=True)
    class Meta: model = AnonymousPost; fields = ('id', 'author', 'content', 'image', 'created_at', 'updated_at', 'tags')
class FriendSerializer(serializers.ModelSerializer):
    class Meta: model = FriendRelation; fields = ('id', 'user_from', 'user_to', 'is_accepted', 'status', 'created_at'); read_only_fields = ('user_from', 'status')
class LocationSerializer(serializers.ModelSerializer):
    class Meta: model = UserLocation; fields = ('latitude', 'longitude', 'is_sharing', 'updated_at')
class ShareSerializer(serializers.ModelSerializer):
    class Meta: model = LocationShare; fields = ('id', 'shared_with', 'expires_at', 'is_active', 'created_at'); read_only_fields = ('owner', 'location')
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta: model = AnonUser; fields = ('username', 'email', 'password')
    def create(self, data):
        password = data.pop('password'); user = AnonUser(**data); user.set_password(password); user.save(); return user
