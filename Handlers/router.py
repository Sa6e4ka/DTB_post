from aiogram import F, Router, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import  Message, CallbackQuery

from dotenv import load_dotenv, find_dotenv
from typing import Union
from io import BytesIO
import os

from Loggs import error_handler_func
from Auxiliaries import MainState, scheduler, schedule_post, S3Client



# Start Router
router_ = Router()

find_dotenv(".env")
load_dotenv()
s3 = S3Client(
    access_key=os.environ.get("AWS_ACCESS_KEY"),
    secret_key=os.environ.get("AWS_SECRET_KEY"),
    bucket_name=os.environ.get("AWS_BUCKET_NAME")
)

    
@router_.message(StateFilter(None, MainState.main), F.video)
@error_handler_func
async def handle_video(message: Message, state: FSMContext, bot: Bot):
    
    state_data = await state.get_data()
    file_id = message.video.file_id

    file = await bot.get_file(file_id)

    # Реализация потоковой передачи данных для того, чтобы миновать загрузку видео на устройство
    bio = BytesIO()
    await bot.download_file(file.file_path, destination=bio)
    bio.seek(0)  

    # Удаление и загрузка видео на бакете 
    await s3.delete_file("meme.m4")
    await s3.upload_file(object_name="meme.mp4", content=bio)

    # Логика для сохрания id видео в машину состояний
    if "videos" in state_data.keys():
        state_data["videos"].append(file_id)
        queue_num = len(state_data["videos"])
        
    else:
        await state.update_data(videos = [file_id])
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

