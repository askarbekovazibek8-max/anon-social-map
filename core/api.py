from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import AnonUser, AnonymousPost, FriendRelation, UserLocation, LocationShare
from .serializers import *

class PostViewSet(viewsets.ModelViewSet):
    queryset = AnonymousPost.objects.filter(is_hidden=False).prefetch_related('tags', 'author')
    serializer_class = PostSerializer
    def perform_create(self, serializer): serializer.save(author=self.request.user)
    def get_permissions(self): return [permissions.IsAuthenticated()] if self.action in ('create','update','partial_update','destroy') else [permissions.AllowAny()]
    def perform_update(self, serializer):
        if self.get_object().author != self.request.user: raise permissions.PermissionDenied()
        serializer.save()
    def perform_destroy(self, instance):
        if instance.author != self.request.user: raise permissions.PermissionDenied()
        instance.delete()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnonUser.objects.all(); serializer_class = PublicUserSerializer; permission_classes = [permissions.AllowAny]; lookup_field = 'anon_code'
class FriendViewSet(viewsets.ModelViewSet):
    serializer_class = FriendSerializer; permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return FriendRelation.objects.filter(user_from=self.request.user) | FriendRelation.objects.filter(user_to=self.request.user)
    def perform_create(self, serializer): serializer.save(user_from=self.request.user)
class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer; permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return UserLocation.objects.filter(user=self.request.user)
    def perform_create(self, serializer): serializer.save(user=self.request.user)
    def perform_update(self, serializer): serializer.save(user=self.request.user)
class ShareViewSet(viewsets.ModelViewSet):
    serializer_class = ShareSerializer; permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return LocationShare.objects.filter(owner=self.request.user)
    def perform_create(self, serializer): serializer.save(owner=self.request.user, location=self.request.user.location)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    serializer = RegisterSerializer(data=request.data); serializer.is_valid(raise_exception=True); serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
