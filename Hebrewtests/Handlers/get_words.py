'''
Получение списка слов из словаря пользователя, сохранение новой темы, переход на сайт pealim.com
'''
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import  Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_get_all_words, orm_save_theme

from Auxiliaries import Theme, button, pealimKB, error_handler

# Words Router
words_router = Router()


'''
Обработчик команды для получения списка слов из лочного словаря
'''
@words_router.message(StateFilter(None), Command("words"))
@error_handler
async def get_all_words(message: Message, session : AsyncSession):
    words = await orm_get_all_words(session=session, chat_id=message.chat.id) 
    
    string = ""
    for i, k in words[0].items():
        string += f"<b>{i} : {k}</b>\n\n"
    
    await message.answer(f"{string}\nКоличество слов в твоем словаре: <b>{words[1]}</b>", reply_markup=button(["Главное меню"]))


'''
Обработчик кнопки добавления темы
'''
@words_router.callback_query(F.data == "Добавить тему")
@error_handler
async def save_themes_on_button(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введи название темы", reply_markup=button(["Отмена"]))
    await state.set_state(Theme.first)


'''
Обработчик команды для добавления темы
'''
@words_router.message(Command("addtheme"))
@error_handler
async def save_themes(message: Message, state: FSMContext):
    await message.answer("Введи название темы", reply_markup=button(["Отмена"]))
    await state.set_state(Theme.first)


'''
Обработчие сообщения для сохранения темы
'''
@words_router.message(StateFilter(Theme.first), F.text)
@error_handler
async def save_an_themes(message: Message, state: FSMContext, session: AsyncSession):
    # Функция сохранения темы
    await orm_save_theme(session=session, theme_name=message.text.lower())
    await message.answer("Тема успешно добавлена!", reply_markup=button(["Главное меню"]))
    await state.clear()


'''
Обработчик команды для открытия pealim.com 
'''
@words_router.message(Command("pealim"))
@error_handler
async def open_pealim(message: Message):
    await message.answer(
        text= "По кнопке ниже ты можешь перейти на сайт pealim.com\n\n<b>Это очень полезный словарь с огромной базой слов и их форм</b>",
        reply_markup=pealimKB.as_markup()
    )