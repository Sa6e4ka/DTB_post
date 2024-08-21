'''
Хендлеры приветствия и кнопок перехода в главное меню
'''
from aiogram import F, Router, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import  Message, CallbackQuery

from typing import Union

from Loggs import error_handler_func
from Auxiliaries import MainState, scheduler, schedule_post

# Start Router
router_ = Router()

    
@router_.message(StateFilter(None, MainState.main), F.video)
@error_handler_func
async def handle_video(message: Message, state: FSMContext, bot: Bot):
    
    state_data = await state.get_data()
    file = message.video.file_id

    if "videos" in state_data.keys():
        state_data["videos"].append(file)
        queue_num = len(state_data["videos"])
        
    else:
        await state.update_data(videos = [file])
        await state.set_state(MainState.main)

        state_data = await state.get_data()
        queue_num = len(state_data["videos"])

    for i, video in enumerate(state_data["videos"]):
        time = await schedule_post(video, bot, i)

    await message.answer(f"Ваше видео успешно добавлено в очередь для отправки.\n\nНомер в очереди: <b>{queue_num}</b>\n\nОно опубликуется\n\n<b>{time}</b>")
     

@router_.message(StateFilter(None, MainState.main), Command("queue"))
async def queue(message: Message, state: FSMContext):
    state_data = await state.get_data()
    
    if "videos" in state_data.keys():
        await message.answer(
            text=f"Количество видео в очереди: {len(state_data["videos"])}"
        )
        return
    
    await message.answer("Видео в очереди пока что нет!")


@router_.callback_query(F.data == "Перезапустить бота")
@router_.message(StateFilter(None, MainState.main), Command("clear"))
async def queue_clear(message_or_call: Union[Message, CallbackQuery], state: FSMContext):
    scheduler.remove_all_jobs()
    await state.update_data(videos = [])

    if type(message_or_call) is Message:
        await message_or_call.answer("Очередь успешно очищена!")
        return
    await message_or_call.message.answer("Очередь успешно очищена!")

