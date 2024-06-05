'''
Сохранение слов в личный словарь пользователя
'''
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter,  or_f

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_save_word

from Auxiliaries import Savewords, button, error_handler


# Save Personal Router
save_personal_router = Router()
 

'''
Обработчик нажатия кнопки для сохранения слова в личный словарь пользователя
'''
@save_personal_router.callback_query(or_f(F.data == 'Добавить слово в свой словарь', F.data == "Загрузить еще слово"))
@error_handler
async def enter_eng_word_byb(call: CallbackQuery, state: FSMContext):
    await state.set_state(Savewords.Hebrew)
    await call.answer()
    await call.message.edit_text('Напиши слово на Иврите:', reply_markup=button(["Отмена"]))


'''
Обработчик команды для сохранения слов в личный словарь
'''
@save_personal_router.message(StateFilter(None) ,Command('saveword'))
@error_handler
async def enter_eng_word(message: Message, state: FSMContext):
    await state.set_state(Savewords.Hebrew)
    await message.answer('Напиши слово <b>на Иврите</b>:')
    
    
'''
Сохранение в словарь состояния слова на иврите и chat_id пользователя
'''
@save_personal_router.message(StateFilter(Savewords.Hebrew), F.text)
@error_handler
async def enter_rus_word_orm(message: Message, state: FSMContext):
    await state.update_data(word = message.text.lower(), chat_id = message.chat.id)
    await message.answer('Напиши <b>перевод</b> этого слова:')
    await state.set_state(Savewords.Translate)

    
'''
Сохранение в словарь состояния перевода слова
'''
@save_personal_router.message(StateFilter(Savewords.Translate), F.text)
@error_handler
async def enter_rus_word_orm(message: Message, state: FSMContext):
    await state.update_data(translation = message.text.lower())
    await message.answer('Теперь напиши <b>транскрибцию</b> этого слова в произвольной форме')
    await state.set_state(Savewords.Transcription)


'''
Сохранения в словарь состояния транскрипции слова
Сохранения слова в таблице
'''
@save_personal_router.message(StateFilter(Savewords.Transcription), F.text)
@error_handler
async def saveword_orm_with_translation(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(transcription = message.text.lower())
    sd = await state.get_data()
    # Функция сохранения слова в таблице
    await orm_save_word(session=session, data=sd)

    await state.clear()
    await message.answer('Слово успешно сохранено в твой личный словарь!\n\n<b>Теперь ты можешь учить его и остальные слова из своего словаря 👇</b>', reply_markup=button(["Учить слова", "Загрузить еще слово"]))
   

