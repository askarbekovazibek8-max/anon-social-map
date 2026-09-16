from django.core.management.base import BaseCommand
from core.models import AnonUser, AnonymousPost, Tag, FriendRelation, UserLocation

class Command(BaseCommand):
    help = 'Создаёт безопасные демонстрационные данные без реальных персональных данных'
    def handle(self, *args, **options):
        users=[]
        for index in range(1, 4):
            user, created = AnonUser.objects.get_or_create(username=f'demo_user_{index}', defaults={'email': f'demo{index}@example.invalid', 'pseudonym': f'Observer-{index:02d}'})
            if created: user.set_password('DemoPassword123!'); user.save()
            users.append(user)
        tags=[Tag.objects.get_or_create(name=name)[0] for name in ('bishkek','news','event','help','traffic')]
        texts=['Новая неделя и новые наблюдения города.', 'В районе центра открылась небольшая выставка.', 'Будьте внимательны на дорогах после дождя.']
        for user, text in zip(users, texts):
            post, _ = AnonymousPost.objects.get_or_create(author=user, content=text)
            post.tags.set(tags[:2])
        FriendRelation.objects.get_or_create(user_from=users[0], user_to=users[1], defaults={'is_accepted': True, 'status': 'accepted'})
        UserLocation.objects.get_or_create(user=users[0], defaults={'latitude': 42.8746, 'longitude': 74.5698, 'is_sharing': False})
        self.stdout.write(self.style.SUCCESS('Демо-данные созданы.'))
