from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
urlpatterns = [
 path('', views.home, name='home'), path('register/', views.register, name='register'), path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'), path('logout/', LogoutView.as_view(), name='logout'),
 path('dashboard/', views.dashboard, name='dashboard'), path('feed/', views.feed, name='feed'), path('posts/new/', views.post_create, name='post_create'), path('posts/<int:pk>/', views.post_detail, name='post_detail'), path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'), path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
 path('friends/', views.friends, name='friends'), path('friends/<int:pk>/<str:action>/', views.friend_action, name='friend_action'), path('map/', views.map_view, name='map'), path('map/location/', views.save_location, name='save_location'), path('privacy/', views.privacy, name='privacy'), path('profile/<uuid:anon_code>/', views.profile, name='profile'), path('<str:page>/', views.info, name='info'),
]
