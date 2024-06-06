from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from Database.models import Words, User, ThemedWords, Themes, Competition

from Loggs import logger

'''
Функция для получения id пользователя
'''
async def orm_get_user_id(session: AsyncSession, chat_id) -> str:
    user_query = select(User.user_id).where(User.chat_id == chat_id)
    user_result  = await session.execute(user_query)
    return user_result.scalars().first()


'''
Функция orm_add_user для добавления пользователя в базу данных
'''
async def orm_add_user(session: AsyncSession, username: str, chat_id: str) -> bool: 
# Проверка на наличие пользователя в базе при вводе команды регистарции
    try:
        query = select(User).where(User.chat_id == chat_id)
        result = await session.execute(query)

        if result.scalars().first(): 
            logger.info(f"Пользователь {username} попытался зарегистрироваться повторно") 
            return 
        
    # Добавление нового пользователя в случае его отсутствия в базе
        user = User(
            username = username,
            chat_id = chat_id
        )

        session.add(user)
        await session.commit()

        id = await orm_get_user_id(session=session, chat_id=chat_id)

        user_compete = Competition(
            global_points = 0,
            global_attempts = 0,
            global_percentage = 0,
            user_id = id
        )

        session.add(user_compete)
        await session.commit()

    except Exception as e:
        print(e)


'''
Функция сохранения слов в личный словарь пользователей
'''
async def orm_save_word(data : dict, session : AsyncSession) -> None:
# Получение id пользователя 
    id = await orm_get_user_id(session=session, chat_id=data["chat_id"])

# Запрос на выборку слова из таблицы
    querry = select(Words.word).where(Words.word == data['word'], Words.user_id == id).limit(1)
    result = await session.execute(querry)

# Проверка наличия слова в таблице
    if result.scalars().first():

    # Если слово в таблице имеется, то обновляем данные о нем (само слово и перевод)
        update_query = update(Words).where(Words.word == data['word']).values(translation = data['translation'])
    
        await session.execute(update_query)
        await session.commit()
    
# Сохраняем новое слово, его перевод и юзера в таблицу
    objects = Words(
        word = data['word'],
        translation = data['translation'],
        transcription = data["transcription"],
        user_id = id
    )

    session.add(objects)
    await session.commit()


'''
Функция для получения случайного слова из таблицы пользователя
'''
async def orm_get_rand_personal_word(session: AsyncSession, chat_id : str) -> list:
# Получение id пользователя
    id = await orm_get_user_id(session=session, chat_id=chat_id)

# Сортировка слов в случайном порядке и выборка одного элемента
    querry = select(Words).where(Words.user_id == id).order_by(func.random()).limit(1)
    
    result = await session.execute(querry)
    scl = result.scalars().first()

# возврат списка со словом и его переводом
    return scl.word, scl.translation, scl.transcription


'''
Функция для получения списка слов для пользователя
'''
async def orm_get_all_words(session : AsyncSession, chat_id : str) -> list:

# Получение Id пользователя
    id = await orm_get_user_id(session=session, chat_id=chat_id)

# Получение списка слов
    query_words_list = select(Words.word, Words.translation).where(Words.user_id == id).order_by(Words.word.asc())
    result = await session.execute(query_words_list)

    word_list = {row[0]: row[1] for row in result.fetchall()}

# Получения количества слов в списке пользователя
    query_count_words = select(func.count(Words.word)).where(Words.user_id == id)
    count_result = await session.execute(query_count_words)
    quantity = count_result.scalar_one()

    
    return word_list, quantity


'''
Функция удаления слова
'''
async def orm_delete_word(session : AsyncSession, word, chat_id) -> None:
# Получение id Пользователя
    id = await orm_get_user_id(session=session, chat_id=chat_id)

    query = select(Words.word).where(Words.word == word, Words.user_id == id)
    result = await session.execute(query)

    if result.scalars().first():
    # Запрос удаления слова
        query = delete(Words).where(Words.word == word, Words.user_id == id)
        await session.execute(query)
        await session.commit()
        return
    return "Такого слова в твоем словаре нет 😨"


'''
Функция для сохранения слов по определенной теме
'''
async def orm_save_themed_word(session : AsyncSession, data : dict) -> None:

    query = select(Themes.theme_id).where(Themes.theme_name == data["theme"])
    result = await session.execute(query)

    id = result.scalars().first()

    word = ThemedWords(
        word = data["word"],
        translation = data["translation"],
        transcription = data["transcription"],
        theme_id = id
    )
    session.add(word)
    await session.commit()


'''
Функция для получения ай ди темы по назанию
'''
async def orm_get_theme_id(session : AsyncSession, theme : str):
    query = select(Themes.theme_id).where(Themes.theme_name == theme).limit(1)

    exc = await session.execute(query)
    return exc.scalars().first()


'''
Функция для получения списка слов по определенной теме
'''
async def orm_get_themed_words_list(session : AsyncSession, theme : dict) -> list:
    # Получение Id пользователя
    id = await orm_get_theme_id(session=session, theme=theme["theme"])

# Получение списка слов
    query_words_list = select(ThemedWords.word, ThemedWords.translation).where(ThemedWords.theme_id == id).order_by(ThemedWords.word.asc())
    result = await session.execute(query_words_list)

    word_list = {row[0]: row[1] for row in result.fetchall()}

# Получения количества слов в списке пользователя
    query_count_words = select(func.count(ThemedWords.word)).where(ThemedWords.theme_id == id)
    count_result = await session.execute(query_count_words)
    quantity = count_result.scalar_one()

    return word_list, quantity


'''
Функция для случайной выборки слова по определенной теме
'''
async def orm_get_random_themed_word(session : AsyncSession, data : dict) -> str:
    id = await orm_get_theme_id(session=session, theme = data["theme"])

    query = select(ThemedWords).where(ThemedWords.theme_id == id).order_by(func.random()).limit(1)
    exc = await session.execute(query)

    result = exc.scalars().first()

    print(result.word)

    return result.word, result.translation, result.transcription


'''
Функция для добавления новой темы
'''
async def orm_save_theme(session : AsyncSession, theme_name : str) -> None:
    theme = Themes(
        theme_name = theme_name
    )

    session.add(theme)
    await session.commit()


'''
Функция для получения списка тем
'''
async def orm_get_theme_list(session : AsyncSession):
    query = select(Themes.theme_name).order_by(Themes.theme_name.asc())
    result = await session.execute(query)
    result_fetch = result.fetchall()

    themes_list = []
    for i in result_fetch:
        themes_list.append(i[0])

    return themes_list


'''
Функция для получения случайного слова из общей таблицы
'''
async def orm_get_rand_global_word(session: AsyncSession):
    query = select(ThemedWords).order_by(func.random())

    execution = await session.execute(query)
    result = execution.scalars().first()

    return result.word, result.translation, result.transcription

'''
Функция для подсчета слов в общей таблице (нужно для того, чтобы открыть соревновательный режим, когда в таблице будет больше 50 слов)
'''
async def orm_count_all_words(session: AsyncSession):
    query = select(func.count(ThemedWords.word))

    execution = await session.execute(query)
    result = execution.scalar()

    return result


'''
Функция для получения соревновательных данных о пользователе
'''
async def orm_get_user_compete_information(session: AsyncSession, id : str) -> dict:

    query = select(Competition).where(Competition.user_id == id)
    execution = await session.execute(query)
    result = execution.scalars().first()

    point_dict = {
        "points" : result.global_points,
        "attempts" : result.global_attempts,
        "percentage" : round(result.global_percentage, 2) 
    }

    return point_dict


'''
Функция для обновления данных в таблице Competition 
''' 
async def orm_update_points(session: AsyncSession, data: dict) -> None:
    id = await orm_get_user_id(session=session, chat_id=data["chat_id"])
    point_info  = await orm_get_user_compete_information(session=session, id=id)

    query = update(Competition).where(Competition.user_id == id).values(
        global_points = point_info["points"] + data["points"],
        global_attempts = point_info["attempts"] + data["attempts"],
        global_percentage = round(((point_info["points"] + data["points"]) / (point_info["attempts"] + data["attempts"])), 2)
    )

    await session.execute(query)
    await session.commit()


'''
Функция для получения топ пользователей 
'''
async def orm_get_top_users(session: AsyncSession):

    query1 = (
        select(Competition.user_id)
        .order_by(
            desc(Competition.global_points), 
            desc(Competition.global_percentage)
        )
    )

    execution = await session.execute(query1)
    result = execution.scalars().all()
    
    usernames = []

    for i in result:
        query2 = select(User.username).where(User.user_id == i)

        execution2 = await session.execute(query2)
        usernames.append(execution2.scalars().first())
    
    users_points = []

    for i in result:
        query3 = (
        select(
            Competition 
        )
        .where(
            Competition.user_id == i
        )
    )   
        
        execution = await session.execute(query3)
        fine = execution.scalars().first()

        data_list = [
            fine.global_points, 
            fine.global_percentage
        ]
        users_points.append(data_list)

    top_dict = {}

    for i, k in zip(usernames, users_points):
        top_dict[i] = k 
    
    return top_dict


'''
Функция удаления слова из общей таблицы
'''
async def orm_delete_themed(session: AsyncSession, word: str) -> None:
    query_get = (
        select(ThemedWords.word)
        .where(
            ThemedWords.word == word
        )
    )

    execution = await session.execute(query_get)
    result = execution.scalars().first()
    if result:    
        query_del = (
            delete(ThemedWords)
            .where(
                ThemedWords.word == word
            )
        )

        await session.execute(query_del)
        await session.commit()
        return
    
    raise AttributeError
