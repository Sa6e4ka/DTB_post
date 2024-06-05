'''
Режим соревнований
'''
from asyncio import sleep

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import  Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_get_rand_global_word, orm_update_points, orm_get_top_users, orm_count_all_words

from Auxiliaries import Competition, button, error_handler, intro
from Loggs import logger


# Compete router
compete_router = Router()


'''
Инициализация режима соревнований в зависимости от количества слов в общем словаре
А так же в зависимости от способа вызова - нажатием кнопки или командой
'''
async def check_compete_availability(session: AsyncSession, message_or_call, is_callback=False):
    count = await orm_count_all_words(session=session)
    # Если слов в общем словаре меньше 50, то режим недоступен
    if count < 50:
        response_text = "Рейтинговый режим станет доступным, когда размер общего словаря превысит 50 слов"
        reply_markup = button(
            [
                "Узнать больше о соревнованиях",
                "Главное меню"
            ]
        )
        if is_callback:
            await message_or_call.message.edit_text(
                response_text,
                reply_markup=reply_markup
            )
        else:
            await message_or_call.answer(
                response_text,
                reply_markup=reply_markup
            )
        return False
    
    reply_markup = button(
        [
            "Начать", 
            "Главное меню"
        ]
    )
    if is_callback:
        await message_or_call.answer()
        await message_or_call.message.edit_text(
            intro,
            reply_markup=reply_markup
        )
    else:
        await message_or_call.answer(
            intro,
            reply_markup=reply_markup
        )
    return True


'''
Функция для отправки топ игроков
'''
async def send_top_users(session: AsyncSession, message_or_call, is_callback=False):
    top = await orm_get_top_users(session=session)
    
    string = "Топ игроков за все время:\n\n"
    for i, z in zip(top.items(), range(1, len(top) + 1)):
        string += f"<b>{z} место</b>\n{i[0]} - {i[1][0]} баллов.\nПроцент выполнения - {i[1][1] * 100}%\n\n"
    
    reply_markup = button(
        [
            "Главное меню"
        ]
    )
    
    if is_callback:
        await message_or_call.message.edit_text(
            text=string,
            reply_markup=reply_markup
        )
        return
    
    await message_or_call.answer(
        text=string,
        reply_markup=reply_markup
    )


'''
Обработчик команды для отправки топа игроков
'''
@compete_router.message(Command("top"))
@error_handler
async def get_users_top(message: Message, session: AsyncSession):
    await send_top_users(session, message)


'''
Обработчик нажатия кнопки для просмотра топа игроков
'''
@compete_router.callback_query(F.data == "Топ игроков")
@error_handler
async def top_on_button(call: CallbackQuery, session: AsyncSession):
    await send_top_users(session, call, is_callback=True)


'''
Обработчик команды /compete - режим соревнования
'''
@compete_router.message(Command("compete"))
@error_handler
async def compete1(message: Message, session: AsyncSession):
    await check_compete_availability(session, message)


'''
Обработчик нажатия на кнопку для вхождения в режим соревнования
'''
@compete_router.callback_query(F.data == "Рейтинговая игра")
@error_handler
async def compete2(call: CallbackQuery, session: AsyncSession):
    await check_compete_availability(session, call, is_callback=True)


'''
До тех пор пока соревнования не работают выдается мануал
'''
@compete_router.callback_query(F.data == "Узнать больше о соревнованиях")
@error_handler
async def compete_info(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        text= intro,
        reply_markup=button(["Главное меню"])
    )


'''
Начало соревнований - получение первого слова и запись первой попытки.
'''
@compete_router.callback_query(F.data == "Начать")
async def compete_first(call : CallbackQuery, session: AsyncSession, state: FSMContext):
    try:
        # Функция получения случайного слова из общей таблицы
        word = await orm_get_rand_global_word(session=session)
        await state.set_state(Competition.Translate)

        # Обновление словаря состояния
        await state.update_data(
            word = word[0],
            translation = word[1], 
            transcription = word[2], 
            chat_id = call.message.chat.id,
            points = 0,
            attempts = 1
        )

        # Отправка слова
        await call.message.edit_text(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Не знаю', "Остановить игру"]))
    # Проверка на наличие слов в словаре
    except AttributeError as e:
        await call.message.edit_text("Кажется, что в словаре еще нет слов по этой теме 🤷‍♂️\n\nЕсли после добавления слова возникнет такая же ошибка, то обязательно напиши @@Megagigapoopfart", reply_markup=button(["Добавить слово в свой словарь"]))
        await state.clear()
        logger.debug(f'Пользователь воспользовался командой /learnwords не загрузив слов в словарь, чем вызвал ошибку в функции learn: {e}')


'''
Вотрой шаг - проверка правильности введения слова и отправка нового.
Прибавление балла (или его не прибавление) и попытки к счетчику
'''
@compete_router.message(StateFilter(Competition.Translate), F.text)
@error_handler
async def compete_second(message: Message, state: FSMContext, session: AsyncSession):
     
    # Получение текущих баллов
    state_data = await state.get_data()
    word = await orm_get_rand_global_word(session=session)

    await state.update_data(translation = word[1], transcription = word[2], word = word[0]) 
    
    if message.text.lower() == state_data["translation"]:
        await message.answer("<b>Правильно!</b> 🥳\n\nЛови следующее слово 👇")
        await state.update_data(points = state_data["points"] + 1, attempts = state_data["attempts"] + 1)  
    else:
        await message.answer(f'<b>Неправильно</b> 😨\n\n{state_data["translation"]} - [{state_data["transcription"]}]')
        await state.update_data(attempts = state_data["attempts"] + 1)  
    
    await sleep(1)
    await message.answer(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Не знаю', "Остановить игру"]))
    

'''
Кнопка пропуска слова
'''
@compete_router.callback_query(F.data == 'Не знаю')
@error_handler
async def skip(call : CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()

    # Получение случайного слова
    word = await orm_get_rand_global_word(session=session)
    state_data = await state.get_data()

    await state.set_state(Competition.Translate)
    # Прибавление количества попыток
    await state.update_data(
        word = word[0],
        translation = word[1], 
        transcription = word[2], 
        chat_id = call.message.chat.id,
        attempts = state_data["attempts"] + 1
    )

    # Отправка перевода и транскрипции слова
    await call.message.edit_text(text=f"{state_data['translation']} - [{state_data['transcription']}]")
    await sleep(2)
    # Отправка нового слова
    await call.message.edit_text(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Не знаю', "Остановить игру"]))


'''
Кнопка остановки игры
'''
@compete_router.callback_query(F.data == "Остановить игру")
@error_handler
async def stop_compete(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()

    state_data = await state.get_data()
    # Обновление баллов в таблице
    await orm_update_points(session=session, data=state_data)
    await state.clear()

    # Отправка набранных пользователем за игру баллов
    await call.message.answer(
        text=f"<b>Твои баллы за эту попытку</b> - {state_data['points']}\n\n<b>Процент выполнения</b> - {(state_data['points'] / state_data['attempts'])*100}%.\n\nТвои баллы записаны в таблицу. Теперь ты можешь посмотреть топ игроков",
        reply_markup=button(
            [
                "Главное меню",
                "Топ игроков"
            ]
        )
    )


'''
Обработчик команды для отправки топа игроков
'''
@compete_router.message(Command("top"))
@error_handler
async def get_users_top(message: Message, session: AsyncSession):
    await send_top_users(session, message)


'''
Обработчик нажатия кнопки для просмотра топа игроков
'''
@compete_router.callback_query(F.data == "Топ игроков")
@error_handler
async def top_on_button(call: CallbackQuery, session: AsyncSession):
    await send_top_users(session, call, is_callback=True)
