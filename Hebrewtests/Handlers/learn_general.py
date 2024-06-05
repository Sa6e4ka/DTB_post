'''
Обучение словам из общегол словаря
'''
from asyncio import sleep

from aiogram import F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import  Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_get_theme_list, orm_get_themed_words_list, orm_get_random_themed_word

from Auxiliaries import LearnThemed, Learn1, button, paginator_for_themed_learn, Pagination2, error_handler
from Loggs import logger


# Global learn Router
global_learn_router = Router()


'''
Функция для выбора темы по нажатию кнопки или вводе комады
'''
async def process_themed_learning(message_or_call, session: AsyncSession):
    themes = await orm_get_theme_list(session=session)
    if len(themes) == 0:
        text = "Похоже, что ни одной темы еще не было добавлено в общий словарь 🤔"
        reply_markup = button(["Главное меню", "Добавить тему"]) if isinstance(message_or_call, CallbackQuery) else button(["Главное меню"])
        
        if isinstance(message_or_call, Message):
            await message_or_call.answer(text=text, reply_markup=reply_markup)
            return
        await message_or_call.message.edit_text(text=text, reply_markup=reply_markup)
        return
    
    KB = await paginator_for_themed_learn(page=0, themes=themes)
    text = "Выбери тему, по которой хочешь учить слова"
    
    if isinstance(message_or_call, Message):
        await message_or_call.answer(text=text, reply_markup=KB)
        return
    await message_or_call.message.edit_text(text=text, reply_markup=KB)


'''
Обработчик нажатия кнопки для выбора темы по которой пользователь
собирается учить слова из общего словаря
'''
@global_learn_router.callback_query(F.data == "Учить по темам")
@error_handler
async def learn_themed_on_button(call: CallbackQuery, session: AsyncSession):
    await process_themed_learning(call, session)


'''
Обработчик команды с той же целью (3 часа ночи я заебался эти комменты писать)
'''
@global_learn_router.message(Command("learnthemed"), StateFilter(None))
@error_handler
async def chosen_choice(message : Message, session: AsyncSession):
    await process_themed_learning(message, session)


'''
Обработчик callback для обеспечения пагинации в выборе темы
'''
@global_learn_router.callback_query(Pagination2.filter())
@error_handler
async def pagination_handler(call: CallbackQuery, callback_data: Pagination2, session: AsyncSession):
    page = callback_data.page  # Получение номера страницы из callback data
    # Функция получения списка тем
    themes = await orm_get_theme_list(session=session)  

    await call.message.edit_reply_markup(reply_markup=await paginator_for_themed_learn(page=page, themes=themes))  # Обновление клавиатуры при нажатии кнопок "вперед" или "назад"


'''
Обработчик нажатия кнопки с темой - предоставление выбора пользователю:
    посмотреть слова по теме списком
    учить слова по теме классическим способом
'''
@global_learn_router.callback_query(F.data.startswith("learn_themed_"))
@error_handler
async def lear_themed(call: CallbackQuery, state: FSMContext):
    await state.set_state(LearnThemed.first)
    await state.update_data(theme = call.data.split("learn_themed_")[-1])

    await call.answer()

    markup = button(["Учить выборкой", "Посмотреть список"])
    await call.message.edit_text(
        text="Ты можешь учить слова случайной выборкой или просто посмотреть их список - выбирай", 
        reply_markup=markup
    )
 

'''
Вывод списка слов по запрашиваемой теме (в будущем планируется добавить пагинацию в зависимости от длины списка)
'''
@global_learn_router.callback_query(or_f(F.data == "Посмотреть список"))
@error_handler
async def get_themed_words_list_on_button(call : CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()
    theme = await state.get_data()
    
    # Функция получения списка слов
    word_list = await orm_get_themed_words_list(session=session, theme=theme)
    
    string = ""
    for i, k in word_list[0].items():
        string += f"<b>{i} : {k}</b>\n\n"
    if len(string) > 0:
        await call.message.edit_text(f"{string}\nКоличество слов в по этой теме: <b>{word_list[1]}</b>", reply_markup=button(["Главное меню"]))
    else:
        await call.message.edit_text("Похоже, что по этой теме слов еще не добавили 😭", reply_markup=button(["Главное меню", "Добавить слова"]))


'''
Обработка сценария для обучения выборко - обработчик нажатия кнопки
'''
@global_learn_router.callback_query(F.data == 'Учить выборкой')
async def learn_byb(call: CallbackQuery, state: FSMContext, session : AsyncSession):
    try:
        theme = await state.get_data()
        # Функция получения случайного слова из общей таблицы
        word = await orm_get_random_themed_word(session=session, data=theme)

        await state.set_state(Learn1.Translate)
        await call.message.edit_text('Сейчас тебе по очереди будут отправляться слова на Иврите, которые были ранее записываны в общий словарь, и ты должен(на) будешь записать их перевод<b>на Русском</b>.\n\nЕсли перевод верный, то тебе будет предложено следующее слово.\n\n<b>Слова из словаря будут выбираться до тех пор пока ты не введешь команду:\n\n/stop</b>')
        await sleep(5)

        await call.message.answer(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Пропустить', "Остановить урок"]))
        await state.update_data(translation = word[1], transcription = word[2], word = word[0])
    except AttributeError as e:
        await call.message.edit_text("Кажется, что в словаре еще нет слов по этой теме 🤷‍♂️\n\nЕсли после добавления слова возникнет такая же ошибка, то обязательно напиши @Megagigapoopfart", reply_markup=button(["Добавить слова", "Главное меню"]))
        logger.debug(f'{e}')
        await state.clear()


'''
Втрой шаг в отгадывании слов - обработчик правильности ввода перевода
'''
@global_learn_router.message(StateFilter(Learn1.Translate), F.text)
@error_handler
async def check(message: Message, state: FSMContext, session: AsyncSession):
      
    state_data = await state.get_data()
    if message.text.lower() == state_data["translation"]:
        await message.answer("<b>Правильно!</b> 🥳\n\nЛови следующее слово 👇")
        
        await sleep(1)

        # Функция получения случайного слова в общей таблице
        word = await orm_get_random_themed_word(session=session, data=state_data)
        await message.answer(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Пропустить', "Остановить урок"]))
        await state.update_data(translation = word[1], transcription = word[2], word = word[0])
        return
    
    await message.answer('<b>Неправильно</b> 😨\n\nПопробуй-ка еще раз!', reply_markup=button(['Пропустить слово']))
    

'''
Обработчик кнопки для пропуска слова
'''
@global_learn_router.callback_query(F.data == 'Пропустить слово')
@error_handler
async def skip(call : CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()

    sd = await state.get_data()
    await call.message.edit_text(
        text=f"Слово - {sd['word']} - [{sd['transcription']}]\n\nПеревод - <b>{sd['translation']}</b>"
    )
    await sleep(3)

    # Функция получения случайного слова в общей таблице
    word = await orm_get_random_themed_word(session=session, data=sd)
    await call.message.edit_text(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Пропустить']))
    
    await state.update_data(translation = word[1], transcription = word[2], word = word[0])
