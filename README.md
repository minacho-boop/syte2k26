# syte2k26
im unemployed
# Games Site

Сайт-каталог компьютерных игр с тестами «какой ты персонаж»,
рекомендациями, донат-ссылками и ролевой моделью доступа.

## Возможности

- Каталог игр с жанрами, авторами и статусом (завершена / в разработке)
- Страница каждой игры: описание, персонажи, ссылки на скачивание и донат
- Тест «какой ты персонаж» — результат определяется по большинству совпадений
- Блок «Вам может понравиться» — рекомендации по общим жанрам
- Регистрация и вход пользователей
- Роли: `reader`, `editor`, `admin`

## Стек

- Python 3.11+
- Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
- SQLite (разработка) / PostgreSQL (продакшен)
- Jinja2-шаблоны

## Установка

```bash
git clone https://github.com/ВАШ_ЛОГИН/games-site.git
cd games-site

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # затем откройте .env и задайте SECRET_KEY
