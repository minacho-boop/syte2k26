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
        action = Genre(name='Экшн')
        strategy = Genre(name='Стратегия')
        simulator = Genre(name='Симулятор')
        horror = Genre(name='Хоррор')
        sandbox = Genre(name='Песочница')
        puzzle = Genre(name='Головоломка')
        stealth = Genre(name='Стелс')
        quest = Genre(name='Квест')
        
        db.session.add_all([rpg, adventure, action, strategy, simulator, horror, sandbox, puzzle, stealth, quest])

        # Создаем авторов
        author1 = Author(name='Capcom')
        author2 = Author(name='Сю Такуми')
        db.session.add_all([author1, author2])
        db.session.commit()

        # Создаем игру
        game1 = Game(
            title='Ace Attorney',
            description='Серия компьютерных игр в жанре квеста, созданная Сю Такуми и изданная Capcom, в которой игроки примеряют на себя роль адвоката в вымышленном судебном сеттинге, основанном на японской системе расследований уголовных дел, чтобы добиться для своих клиентов вердикта «невиновен», при этом проводя расследования, изучая доказательства и устраивая перекрёстный допрос свидетелям.',
            status='completed',
            download_url='https://store.steampowered.com/curator/44969618-Ace-Attorney-Franchise/',
            donate_url=''
        )
        # Привязываем жанры и авторов
        game1.genres.extend([rpg, quest])
        game1.authors.extend([author1])
        db.session.add(game1)
        db.session.commit()

        # Создаем персонажей для игры
        char1 = Character(game_id=game1.id, name='Феникс Райт', description='Адвокат-ветеран, руководящий юридическим бюро «Агентство Райта по любым делам». В основном специализируется на уголовном судопроизводстве, и известен благодаря своему таланту «обзора дела под другим углом», что помогает ему выиграть те дела, которые многим казались заведомо проигрышными.')
        char2 = Character(game_id=game1.id, name='Майа Фей', description='Майя энергичная, задорная, возбудимая и общительная девушка. Она излучает детскую индивидуальность, будучи одновременно импульсивно любопытной и легко сбиваемой с толку. Она часто действует не задумываясь, пытается без коснуться до любых предметов, что часто не имеет смысла. Мастер техники призыва духов деревни Курайн и, впоследствии, глава клана Фей. Близкий друг адвоката Феникса Райта, а также его главный помощник в течение большей части карьеры.')
        char3 = Character(game_id=game1.id, name='Майлз Эджворт', description='Эджворт обычно спокоен и уравновешен, но считается снобом из-за своей холодной, безжалостной и в целом отчуждённой натуры. У него определённая нехватка социальных навыков и такта, что делает его очень неуверенным и неловким в окружении. Генеральный прокурор. В течение первых четырёх лет карьеры он добился идеального рекорда в судебных процессах, будучи готовыми сделать практически всё для получения обвинительного приговора. Его поражение в суде от руки его друга детства Феникса Райта послужило основой для пересмотра взглядов на его работу. ')
        db.session.add_all([char1, char2, char3])
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
