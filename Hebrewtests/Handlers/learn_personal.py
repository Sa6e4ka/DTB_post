'''
Режим обучения словам из личного словаря пользователя
'''

from asyncio import sleep

from aiogram import F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import  Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from Database import orm_get_rand_personal_word

from Auxiliaries import button, error_handler, Learn


# Learn Router
learn_router = Router()


'''
Функция для режима обучения словам из личного словаря пользователя.
Обрабатывает 2 сценария:
    Ввод команды
    Нажатие кнопки
'''
async def process_learn(state: FSMContext, session: AsyncSession, chat_id: int, message_or_call):
    try:
        word = await orm_get_rand_personal_word(session=session, chat_id=chat_id)
        await state.set_state(Learn.Translate)
        intro_message = (
            'Сейчас тебе отправится слово на Иврите, которое ты ранее записывал(а) в свой личный словарь, '
            'и ты должен(на) будешь записать его перевод <b>на Русском</b>.\n\n'
            'Если перевод верный, то тебе будет предложено следующее слово.\n\n'
            '<b>Слова из твоего словаря будут выбираться до тех пор пока ты не нажмешь кнопку или не введешь команду /stop</b>'
        )
        
        if isinstance(message_or_call, Message):
            await message_or_call.answer(intro_message)
            await sleep(5)

            await message_or_call.answer(
            text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:",
            reply_markup=button(text=['Пропустить', "Остановить урок"])
        )
            await state.update_data(translation=word[1], transcription=word[2], word=word[0])
            return
        
        await message_or_call.message.edit_text(intro_message)
        await sleep(5)
        await message_or_call.message.edit_text(
            text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:",
            reply_markup=button(text=['Пропустить', "Остановить урок"])
        )
        await state.update_data(translation=word[1], transcription=word[2], word=word[0])
    except AttributeError:
        error_messaage = "Кажется, в твоем словаре нет слов 🤷‍♂️"
        if isinstance(message_or_call, Message):
            await message_or_call.answer(error_messaage, reply_markup=button(["Главное меню", "Добавить слово в свой словарь"]))
            return
        await message_or_call.message.edit_text(error_messaage, reply_markup=button(text=['Главное меню', "Добавить слово в свой словарь"]))


'''
Обработчик нажатия кнопки для остановки режима обучения
'''
@learn_router.callback_query(or_f(F.data == "Остановить урок"))
@error_handler
async def stop_lesson(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text="Урок окончен!\n\nНадеюсь ты не станешь так быстро сдаваться 😈", reply_markup=button(["Главное меню"]))


'''
Обработчик нажатия кнопки для начала режима обучения
'''
@learn_router.callback_query(or_f(F.data == 'Учить слова', F.data == "Учить свои слова"))
@error_handler
async def learn_byb(call: CallbackQuery, state: FSMContext, session : AsyncSession):
    await process_learn(state, session, call.message.chat.id, call)


'''
Обработчик ввода команды для начала режима обучения
'''
@learn_router.message(StateFilter(None), Command('learnwords'))
@error_handler
async def learn(message: Message, session: AsyncSession, state: FSMContext):
    await process_learn(state, session, message.chat.id, message)


'''
Обработчик введенного пользователем перевода:
    Проверяет его и дает ввести заново если он не правильный
'''
@learn_router.message(StateFilter(Learn.Translate), F.text)
@error_handler
async def check(message: Message, state: FSMContext, session: AsyncSession):
     
    state_data = await state.get_data()
    if message.text.lower() == state_data["translation"]:
        await message.answer("<b>Правильно!</b> 🥳\n\nЛови следующее слово 👇")
        
        await sleep(1)

        # Получение случайного слова из личной таблицы пользователя
        word = await orm_get_rand_personal_word(session=session, chat_id=message.chat.id)
        await message.answer(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Пропустить', "Остановить урок"]))
        await state.update_data(translation = word[1], transcription = word[2], word = word[0])
        return
    
    await message.answer('<b>Неправильно</b> 😨\n\nПопробуй-ка еще раз!', reply_markup=button(['Пропустить', "Остановить урок"]))


'''
Обработчие нажатия кнопки для пропуска слова
'''
@learn_router.callback_query(F.data == 'Пропустить')
@error_handler
async def skip(call : CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()
    sd = await state.get_data()
    await call.message.edit_text(
        text=f"Слово - {sd['word']} - [{sd['transcription']}]\n\nПеревод - <b>{sd['translation']}</b>"
    )
    await sleep(3)
    
    # Получение случайного слова из личной таблицы пользователя
    word = await orm_get_rand_personal_word(session=session, chat_id=call.message.chat.id)
    await call.message.edit_text(text=f"Слово:<b>\n\n{word[0]}</b>\n\nТеперь введи его перевод:", reply_markup=button(text=['Пропустить']))
    
    await state.update_data(translation = word[1], transcription = word[2], word = word[0])
