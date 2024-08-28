from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import  Message, CallbackQuery

from dotenv import load_dotenv, find_dotenv
from typing import Union
from io import BytesIO
import os

from Loggs import error_handler_func
from Auxiliaries import scheduler, schedule_post, S3Client

# Router
router_ = Router()

find_dotenv(".env")
load_dotenv()
s3 = S3Client(
    access_key=os.environ.get("AWS_ACCESS_KEY"),
    secret_key=os.environ.get("AWS_SECRET_KEY"),
    bucket_name=os.environ.get("AWS_BUCKET_NAME")
)

global_state = {}
    
@router_.message(F.video)
@error_handler_func
async def handle_video(message: Message, bot: Bot):
    
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
    if "videos" in global_state.keys():
        global_state["videos"].append(file_id)
        queue_num = len(global_state["videos"])
        
    else:
        global_state["videos"] = [file_id]
        queue_num = len(global_state["videos"])

    for i, video in enumerate(global_state["videos"]):
        time = await schedule_post(video, bot, i, global_state)

    await message.answer(f"Ваше видео успешно добавлено в очередь для отправки.\n\nНомер в очереди: <b>{queue_num}</b>\n\nОно опубликуется\n\n<b>{time}</b>")
     

@router_.message(Command("queue"))
async def queue(message: Message):
    
    if "videos" in global_state.keys():
        await message.answer(
            text=f"Количество видео в очереди: {len(global_state["videos"])}"
        )
        return
    
    await message.answer("Видео в очереди пока что нет!")


@router_.callback_query(F.data == "Перезапустить бота")
@router_.message(Command("clear"))
async def queue_clear(message_or_call: Union[Message, CallbackQuery]):
    print(scheduler.get_jobs())
    scheduler.remove_all_jobs()

    global_state["videos"] = []

    if type(message_or_call) is Message:
        await message_or_call.answer("Очередь успешно очищена\n\nБот перезапущен")
        return
    await message_or_call.message.answer("Очередь успешно очищена!")

