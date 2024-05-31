'''
Удаление слова из словарей
'''
from aiogram import F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import  Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_delete_word, orm_delete_themed

from Auxiliaries import Delete, Delete2, button, error_handler


# Delete Router
delete_router = Router()


'''
Обработчик команды для удаления слова
Предложение выбрать словарь для удаления слова из него
'''
@delete_router.message(StateFilter(None), Command("delete"))
@error_handler
async def choose_dict_to_delete(message : Message, state: FSMContext):
    await state.clear()
    murkup = button(["Из своего словаря", "Из общего словаря", "Главное меню"])
    await message.answer(text="Выбери словарь, из которого хочешь удалить слово", reply_markup=murkup)


'''
Обработчик нажатия кнопок с выбором словаря
'''
@delete_router.callback_query(or_f(F.data == "Из своего словаря", F.data == "Удалить еще слово", F.data == "Из общего словаря", F.data == "Удалить еще", F.data == "Удалить нужное слово", F.data == "Удалить правильное слово")) 
@error_handler
async def choose_on_button(call: CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data in ["Из своего словаря", "Удалить еще слово", "Удалить правильное слово"]: 
        await call.message.edit_text(text="Введи (на Иврите) слово, которое хочешь <b>удалить из своего словаря</b>:")   
        await state.set_state(Delete.Delete)
        return
    
    await call.message.edit_text("Введи (на Иврите) слово, которое хочешь <b>удалить из общего словаря</b>:")
    await state.set_state(Delete2.Delete2)


'''
Удаление слова из личного словаря
'''
@delete_router.message(StateFilter(Delete.Delete), F.text)
@error_handler
async def delete_personal_word(message: Message, state: FSMContext, session: AsyncSession):
        result = await orm_delete_word(word = message.text.lower(), chat_id = message.chat.id, session=session)

        if result is not None:
            await message.answer(result, reply_markup=button(["Удалить правильное слово", "Главное меню"]))
            await state.clear()
            return
        
        await message.answer('Слово было успешно удалено!', reply_markup=button(["Удалить еще слово", "Главное меню"]))
        await state.clear()
   

'''
Удаление слва из общего словаря
'''
@delete_router.message(StateFilter(Delete2.Delete2))
async def delte_global_word(message: Message, state: FSMContext, session: AsyncSession):
    markup=button(["Главное меню","Удалить еще" ])        
    try:
        await orm_delete_themed(session=session, word = message.text.lower())
        await message.answer(text="Слово успешно удалено!", reply_markup=markup)
    except AttributeError:
        await message.answer(text="Этого слова в таблице еще нет 😭",reply_markup=markup)
    await state.clear()

