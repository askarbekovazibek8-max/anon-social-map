from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegisterForm, PostForm, FriendForm, LocationForm, PrivacyForm
from .models import AnonUser, AnonymousPost, FriendRelation, UserLocation, LocationShare, Tag

def home(request): return render(request, 'core/home.html')
def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid(): login(request, form.save()); return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})
@login_required
def dashboard(request):
    friends = FriendRelation.objects.filter(Q(user_from=request.user) | Q(user_to=request.user), is_accepted=True)
    incoming = FriendRelation.objects.filter(user_to=request.user, status='pending')
    return render(request, 'core/dashboard.html', {'my_posts': request.user.posts.all()[:5], 'friends': friends.count(), 'incoming': incoming.count(), 'active_locations': LocationShare.objects.filter(shared_with=request.user, is_active=True, expires_at__gt=timezone.now()).count(), 'latest': AnonymousPost.objects.filter(is_hidden=False)[:8]})

def feed(request):
    posts = AnonymousPost.objects.filter(is_hidden=False).select_related('author').prefetch_related('tags')
    query = request.GET.get('q'); tag = request.GET.get('tag')
    if query: posts = posts.filter(Q(content__icontains=query) | Q(author__pseudonym__icontains=query))
    if tag: posts = posts.filter(tags__name=tag.lstrip('#'))
    from django.core.paginator import Paginator
    return render(request, 'core/feed.html', {'posts': Paginator(posts.distinct(), 8).get_page(request.GET.get('page')), 'tags': Tag.objects.all()})
@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid(): post=form.save(commit=False); post.author=request.user; post.save(); form.save_m2m(); messages.success(request, 'Пост успешно опубликован'); return redirect('feed')
    return render(request, 'core/form.html', {'form': form, 'title': 'Новый анонимный пост'})
@login_required
def post_delete(request, pk):
    post=get_object_or_404(AnonymousPost, pk=pk, author=request.user)
    if request.method == 'POST': post.delete(); messages.success(request, 'Пост удалён')
    return redirect('feed')
@login_required
def post_edit(request, pk):
    post = get_object_or_404(AnonymousPost, pk=pk, author=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save(); messages.success(request, 'Пост обновлён'); return redirect('feed')
    return render(request, 'core/form.html', {'form': form, 'title': 'Редактировать пост'})
def post_detail(request, pk):
    return render(request, 'core/post_detail.html', {'post': get_object_or_404(AnonymousPost, pk=pk, is_hidden=False)})
@login_required
def friends(request):
    form=FriendForm(request.POST or None)
    if form.is_valid():
        target=get_object_or_404(AnonUser, anon_code=form.cleaned_data['anonymous_id'])
        if target == request.user: form.add_error('anonymous_id', 'Нельзя добавить себя.')
        elif FriendRelation.objects.filter(user_from=request.user, user_to=target).exists(): form.add_error(None, 'Запрос уже отправлен.')
        else: FriendRelation.objects.create(user_from=request.user, user_to=target); messages.success(request, 'Запрос отправлен'); return redirect('friends')
    return render(request, 'core/friends.html', {'form':form, 'incoming':FriendRelation.objects.filter(user_to=request.user, status='pending'), 'relations':FriendRelation.objects.filter(Q(user_from=request.user)|Q(user_to=request.user))})
@login_required
def friend_action(request, pk, action):
    relation=get_object_or_404(FriendRelation, pk=pk)
    if relation.user_to != request.user and relation.user_from != request.user: return redirect('friends')
    if action == 'accept' and relation.user_to == request.user: relation.status='accepted'; relation.is_accepted=True; relation.save(update_fields=['status','is_accepted'])
    elif action == 'reject': relation.status='rejected'; relation.save(update_fields=['status'])
    elif action == 'delete': relation.delete()
    return redirect('friends')
@login_required
def map_view(request):
    return render(request, 'core/map.html', {'friends': AnonUser.objects.filter(Q(friends_from__user_to=request.user, friends_from__status='accepted')|Q(friends_to__user_from=request.user, friends_to__status='accepted')).distinct()})
@login_required
def save_location(request):
    form=LocationForm(request.POST or None, instance=getattr(request.user, 'location', None))
    if form.is_valid(): loc=form.save(commit=False); loc.user=request.user; loc.save(); messages.success(request, 'Локация обновлена'); return redirect('map')
    return render(request, 'core/form.html', {'form':form, 'title':'Моя локация'})
@login_required
def privacy(request):
    form=PrivacyForm(request.POST or None, instance=request.user)
    if form.is_valid(): form.save(); messages.success(request, 'Настройки приватности сохранены'); return redirect('privacy')
    return render(request, 'core/form.html', {'form':form, 'title':'Настройки приватности'})
def profile(request, anon_code): return render(request, 'core/profile.html', {'profile':get_object_or_404(AnonUser, anon_code=anon_code).public_profile()})
def info(request, page): return render(request, f'core/{page}.html')
