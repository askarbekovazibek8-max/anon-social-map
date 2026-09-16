import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validate_image(image):
    if image and image.size > 5 * 1024 * 1024:
        raise ValidationError('Изображение не может быть больше 5 MB.')
    if image and image.content_type not in {'image/jpeg', 'image/png', 'image/webp'}:
        raise ValidationError('Разрешены только JPG, PNG и WebP.')


class AnonUser(AbstractUser):
    anon_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    pseudonym = models.CharField(max_length=40, unique=True)
    location_visibility = models.CharField(max_length=20, choices=[('friends', 'Только друзья'), ('selected', 'Выбранные друзья'), ('nobody', 'Никто')], default='friends')
    location_sharing_enabled = models.BooleanField(default=True)
    show_on_map = models.BooleanField(default=False)

    def public_profile(self):
        return {'anonymous_id': str(self.anon_code), 'pseudonym': self.pseudonym,
                'posts_count': self.posts.count(), 'friends_count': self.friends_from.filter(is_accepted=True).count()}

    def __str__(self):
        return self.pseudonym


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    def clean(self):
        self.name = self.name.strip().lower().lstrip('#')
        if not self.name.replace('_', '').isalnum():
            raise ValidationError('Тег может содержать буквы, цифры и _.')
    def __str__(self): return f'#{self.name}'


class AnonymousPost(models.Model):
    author = models.ForeignKey(AnonUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=5000)
    image = models.ImageField(upload_to='posts/%Y/%m/', blank=True, null=True, validators=[validate_image])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at', 'is_hidden'])]
    def __str__(self): return f'Пост {self.pk} от {self.author.pseudonym}'


class FriendRelation(models.Model):
    user_from = models.ForeignKey(AnonUser, on_delete=models.CASCADE, related_name='friends_from')
    user_to = models.ForeignKey(AnonUser, on_delete=models.CASCADE, related_name='friends_to')
    is_accepted = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user_from', 'user_to'], name='unique_friend_request')]
        indexes = [models.Index(fields=['user_to', 'status'])]
    def clean(self):
        if self.user_from_id == self.user_to_id: raise ValidationError('Нельзя добавить себя.')


class UserLocation(models.Model):
    user = models.OneToOneField(AnonUser, on_delete=models.CASCADE, related_name='location')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_sharing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    def clean(self):
        if not -90 <= float(self.latitude) <= 90 or not -180 <= float(self.longitude) <= 180: raise ValidationError('Некорректные координаты.')


class LocationShare(models.Model):
    owner = models.ForeignKey(AnonUser, on_delete=models.CASCADE, related_name='location_shares')
    shared_with = models.ForeignKey(AnonUser, on_delete=models.CASCADE, related_name='received_location_shares')
    location = models.ForeignKey(UserLocation, on_delete=models.CASCADE, related_name='shares')
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'shared_with'], name='unique_location_share')]
        indexes = [models.Index(fields=['shared_with', 'is_active', 'expires_at'])]
    def clean(self):
        if self.owner_id == self.shared_with_id: raise ValidationError('Нельзя делиться с собой.')
    @property
    def currently_active(self): return self.is_active and self.expires_at > timezone.now()
