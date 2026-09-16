from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AnonUser, AnonymousPost, Tag, FriendRelation, UserLocation, LocationShare
@admin.register(AnonUser)
class AnonUserAdmin(UserAdmin):
    list_display = ('pseudonym','anon_code','is_active','date_joined'); search_fields = ('pseudonym','anon_code','username'); ordering = ('-date_joined',)
@admin.register(AnonymousPost)
class PostAdmin(admin.ModelAdmin):
    list_display=('id','author','created_at','is_hidden'); list_filter=('is_hidden','created_at'); search_fields=('content','author__pseudonym'); ordering=('-created_at',)
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin): search_fields=('name',); ordering=('name',)
@admin.register(FriendRelation)
class FriendAdmin(admin.ModelAdmin): list_display=('user_from','user_to','status','created_at'); list_filter=('status',); search_fields=('user_from__pseudonym','user_to__pseudonym')
@admin.register(UserLocation)
class LocationAdmin(admin.ModelAdmin): list_display=('user','latitude','longitude','is_sharing','updated_at'); list_filter=('is_sharing',)
@admin.register(LocationShare)
class ShareAdmin(admin.ModelAdmin): list_display=('owner','shared_with','expires_at','is_active'); list_filter=('is_active',); ordering=('-created_at',)
