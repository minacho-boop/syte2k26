from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'  # для PostgreSQL: 'postgresql://...'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ---------- Ассоциативные таблицы (many-to-many) ----------
game_genre = db.Table('game_genre',
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

game_author = db.Table('game_author',
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)

# ---------- Модели ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='reader')  # admin, editor, reader

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='in_development')  # completed / in_development
    download_url = db.Column(db.String(500))
    donate_url = db.Column(db.String(500))
    genres = db.relationship('Genre', secondary=game_genre, backref='games')
    authors = db.relationship('Author', secondary=game_author, backref='games')
    characters = db.relationship('Character', backref='game', cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='game', cascade='all, delete-orphan')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    options = db.relationship('AnswerOption', backref='question', cascade='all, delete-orphan')

class AnswerOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    character = db.relationship('Character')

# ---------- Загрузка пользователя для Flask-Login ----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Декоратор для проверки ролей ----------
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ---------- Создание таблиц и тестовых данных (при первом запуске) ----------
with app.app_context():
    db.create_all()
    # Раскомментируйте, если нужно заполнить демо-данными:
    # from seed import seed_data
    # seed_data()

# ---------- Маршруты ----------
@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    # «Вам может понравиться»: игры с общими жанрами, кроме текущей
    similar = []
    if game.genres:
        genre_ids = [g.id for g in game.genres]
        similar = Game.query.filter(
            Game.id != game.id,
            Game.genres.any(Genre.id.in_(genre_ids))
        ).limit(4).all()
    return render_template('game.html', game=game, similar=similar)

@app.route('/game/<int:game_id>/quiz', methods=['GET', 'POST'])
def quiz(game_id):
    game = Game.query.get_or_404(game_id)
    if request.method == 'POST':
        scores = defaultdict(int)
        for question in game.questions:
            option_id = request.form.get(f'q{question.id}')
            if option_id:
                option = AnswerOption.query.get(int(option_id))
                if option:
                    scores[option.character_id] += 1
        if not scores:
            flash('Вы не ответили ни на один вопрос.')
            return redirect(url_for('quiz', game_id=game.id))
        winner_id = max(scores, key=scores.get)
        winner = Character.query.get(winner_id)
        return render_template('quiz_result.html', game=game, character=winner, scores=scores)
    return render_template('quiz.html', game=game)

# ---------- Аутентификация ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'reader')  # в реальном проекте роль назначает админ
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Пользователь с таким именем или email уже существует.')
            return redirect(url_for('register'))
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна. Войдите.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверные учётные данные.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ---------- Админ-панель (пример защиты по ролям) ----------
@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
