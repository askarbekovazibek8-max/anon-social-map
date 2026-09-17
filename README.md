# AnonSocial & Map

Анонимная социальная платформа для публикации новостей, поиска друзей и приватного обмена локациями в Бишкеке.

## Технологии
Python, Django, Django ORM, SQLite (готово к PostgreSQL), Django Admin, Forms/ModelForms, DRF, drf-spectacular, Pillow, HTML5/CSS3/JavaScript, Leaflet.js и OpenStreetMap.

## Установка
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Главная: http://127.0.0.1:8000/  | Admin: `/admin/`  | API: `/api/`  | Swagger: `/api/docs/`.

## Production

Для production используются `WhiteNoise`, `gunicorn` и `collectstatic`. На Render применяйте `render.yaml`, задайте `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` и `DJANGO_CSRF_TRUSTED_ORIGINS`, а SQLite и `media/` замените на PostgreSQL и постоянное/object storage. Vercel не рекомендуется для этой конфигурации: его serverless-файловая система не подходит для SQLite и загруженных изображений. Перед deploy выполните `python manage.py check` и `python manage.py collectstatic --noinput`.

## Возможности
Регистрация с анонимным UUID и псевдонимом, приватный профиль, посты с изображениями и тегами, поиск и пагинация, друзья с защитой от дубликатов, карта Бишкека с геолокацией, настройки видимости, безопасные API и администрирование. Локация не публична по умолчанию.

## Структура
`config/` настройки и URL, `core/` модели/forms/views/API/Admin, `templates/` HTML, `static/` CSS/JS, `media/` загрузки, `manage.py` и SQLite база.

Для PostgreSQL замените `DATABASES` в `config/settings.py` и добавьте драйвер `psycopg`.
