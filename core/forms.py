from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import AnonUser, AnonymousPost, Tag, FriendRelation, UserLocation

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = AnonUser; fields = ('username', 'email', 'password1', 'password2')
    def clean_username(self):
        value = self.cleaned_data['username'].strip()
        if len(value) < 3 or not value.replace('_', '').isalnum(): raise ValidationError('Логин: минимум 3 символа, только буквы, цифры и _.')
        return value
    def save(self, commit=True):
        user = super().save(commit=False)
        user.pseudonym = f'Anonymous-{str(user.anon_code)[:8]}'
        if commit: user.save()
        return user

class PostForm(forms.ModelForm):
    tags_text = forms.CharField(required=False, label='Теги', help_text='Например: #news #bishkek')
    class Meta:
        model = AnonymousPost; fields = ('content', 'image', 'tags_text')
    def save(self, commit=True):
        post = super().save(commit=commit)
        names = {x.strip().lstrip('#').lower() for x in self.cleaned_data.get('tags_text', '').split() if x.strip()}
        if commit: post.tags.set([Tag.objects.get_or_create(name=name)[0] for name in names])
        return post

class FriendForm(forms.Form):
    anonymous_id = forms.UUIDField(label='Anonymous ID')

class LocationForm(forms.ModelForm):
    class Meta:
        model = UserLocation; fields = ('latitude', 'longitude', 'is_sharing')

class PrivacyForm(forms.ModelForm):
    class Meta:
        model = AnonUser; fields = ('location_visibility', 'location_sharing_enabled', 'show_on_map')
