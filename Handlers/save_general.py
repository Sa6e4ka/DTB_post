from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter,  or_f

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_save_themed_word, orm_get_theme_list

from Auxiliaries import SaveThemed, button, paginator, Pagination, error_handler


# Save General Router
save_general_router = Router()


'''
Функция для отправки клавиатуры для выбора темы для сохранения слова в общий словарь
'''
async def process_theme_selection(message_or_call, session: AsyncSession):
    themes = await orm_get_theme_list(session=session)
    if len(themes) == 0:
        text = "Похоже, что ни одной темы еще не было добавлено в общий словарь 🤔"
        reply_markup = button(["Главное меню", "Отмена"])
        
        if isinstance(message_or_call, Message):
            await message_or_call.answer(text=text, reply_markup=reply_markup)
            return
        await message_or_call.message.edit_text(text=text, reply_markup=reply_markup)
        return
    
    KB = await paginator(page=0, themes=themes)
    text = "Выбери тему, по которой хочешь загрузить слово"
    
    if isinstance(message_or_call, Message):
        await message_or_call.answer(text=text, reply_markup=KB)
        return
    await message_or_call.message.edit_text(text=text, reply_markup=KB)


'''
Обработчик команды для сохранения слова по теме
'''
@save_general_router.message(Command("saveontheme"))
@error_handler
async def add_ban(message: Message, session: AsyncSession):
    await process_theme_selection(message, session)


'''
Обработчик нажатия кнопки для сохранения слова в общий словарь
'''
@save_general_router.callback_query(or_f(F.data == "Добавить слова", F.data == "Добавить слова по темам"))
async def add_ban_on_button(call: CallbackQuery, session: AsyncSession):
    await process_theme_selection(call, session)


'''
Пагинация кнопок с темами
'''
@save_general_router.callback_query(Pagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination, session: AsyncSession):
    page = callback_data.page  # Получение номера страницы из callback data
    themes = await orm_get_theme_list(session=session)  

    await call.message.edit_reply_markup(reply_markup=await paginator(page=page, themes=themes))  # Обновление клавиатуры при нажатии кнопок "вперед" или "назад"


'''
Обработчик нажатия кнопки с выбранной пользователем темой
'''
@save_general_router.callback_query(or_f(F.data.startswith("theme"), F.data == "Загрузить по той же теме", F.data == "Добавить слово по этой теме"))
async def callback_on_themes(call: CallbackQuery, state: FSMContext):
    await state.set_state(SaveThemed.second)

    if F.data.startswith("theme"):
        theme = call.data.split("_")[-1]
        await state.update_data(theme = theme)
    else:    
        state_data = await state.get_data()
        theme = state_data["theme"]
        await state.update_data(theme=theme)

    await call.answer()
    await call.message.edit_text(text="Введи слово на <b>Иврите</b>")


'''
Сохранения слова на Иврите в словаре состояний
'''
@save_general_router.message(F.text, StateFilter(SaveThemed.second))
async def save_on_theme_third(message : Message, state: FSMContext):
    await state.update_data(
        word = message.text.lower()
    )

    await message.answer(
        text="Введи его перевод <b>на Русский</b>"
    )

    await state.set_state(SaveThemed.third)


'''
Сохранение перевода в словаре состояния
'''
@save_general_router.message(F.text, StateFilter(SaveThemed.third))
async def save_on_theme_fourth(message : Message, state: FSMContext):
    await state.update_data(translation = message.text.lower())
    await message.answer(text="Введи его <b>транскрибцию</b> в произвольном виде.\n\nГлавное, чтобы было понятно как оно читается и было ударением")
    await state.set_state(SaveThemed.fourth)


'''
Сохранение транскрипции в словаре состояния
Сохранение слова в общей таблицы
'''
@save_general_router.message(F.text, StateFilter(SaveThemed.fourth))
async def save_on_theme_fifth(message : Message, state: FSMContext, session : AsyncSession):
    await state.update_data(transcription = message.text.lower())
    state_data = await state.get_data()
    # Сохранение слова
    await orm_save_themed_word(session=session, data=state_data)

    await message.answer(text="Слово успешно сохранено!\n\nТепеь ты можешь приступать к отработке или загрузить еше слова ", reply_markup=button(["Загрузить по той же теме", "Главное меню"]))

