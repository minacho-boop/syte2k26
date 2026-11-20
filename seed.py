from app import app, db, Game, Genre, Author, Character, Question, AnswerOption, User

def seed_data():
    with app.app_context():
        # Очищаем старые данные (если есть)
        db.drop_all()
        db.create_all()

        # Создаем пользователей (Админ, Редактор, Читатель)
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        
        editor = User(username='editor', email='editor@example.com', role='editor')
        editor.set_password('editor123')

        db.session.add_all([admin, editor])
        db.session.commit()

        # Создаем жанры
        rpg = Genre(name='RPG')
        adventure = Genre(name='Приключения')
        db.session.add_all([rpg, adventure])

        # Создаем авторов
        author1 = Author(name='Иван Иванов', bio='Главный геймдизайнер')
        author2 = Author(name='Петр Петров', bio='Сценарист')
        db.session.add_all([author1, author2])
        db.session.commit()

        # Создаем игру
        game1 = Game(
            title='Ace Attorney',
            description='серия компьютерных игр в жанре квеста, созданная Сю Такуми[1] и изданная Capcom, в которой игроки примеряют на себя роль адвоката в вымышленном судебном сеттинге, основанном на японской системе расследований уголовных дел, чтобы добиться для своих клиентов вердикта «невиновен», при этом проводя расследования, изучая доказательства и устраивая перекрёстный допрос свидетелям.',
            status='completed',
            download_url='https://store.steampowered.com/curator/44969618-Ace-Attorney-Franchise/',
            donate_url='https://example.com/donate'
        )
        # Привязываем жанры и авторов
        game1.genres.extend([rpg, adventure])
        game1.authors.extend([author1, author2])
        db.session.add(game1)
        db.session.commit()

        # Создаем персонажей для игры
        char1 = Character(game_id=game1.id, name='Рыцарь', description='Смелый и сильный воин.')
        char2 = Character(game_id=game1.id, name='Маг', description='Умный и владеет магией.')
        db.session.add_all([char1, char2])
        db.session.commit()

        # Создаем тест
        q1 = Question(game_id=game1.id, text='Как вы обычно решаете проблемы?')
        db.session.add(q1)
        db.session.commit()

        # Варианты ответов (привязка к персонажам)
        opt1 = AnswerOption(question_id=q1.id, text='Беру меч и иду напролом', character_id=char1.id)
        opt2 = AnswerOption(question_id=q1.id, text='Ищу обходные пути и читаю книги', character_id=char2.id)
        db.session.add_all([opt1, opt2])
        db.session.commit()

        print("База данных успешно заполнена!")

if __name__ == '__main__':
    seed_data()
