from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .api import PostViewSet, UserViewSet, FriendViewSet, LocationViewSet, ShareViewSet, register_api
router = DefaultRouter()
router.register('posts', PostViewSet, basename='post'); router.register('users', UserViewSet, basename='user'); router.register('friends', FriendViewSet, basename='friend'); router.register('locations', LocationViewSet, basename='location'); router.register('shares', ShareViewSet, basename='share')
urlpatterns = [path('register/', register_api), path('', include(router.urls))]
