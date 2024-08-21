import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from dotenv import load_dotenv
load_dotenv()


API_TOKEN = str(os.environ.get('API_TOKEN'))
GROUP_ID = -4578892217  
SAVE_DIR = "videos" 
CHANNEL_ID = '@daun_type_beat'  

scheduler = AsyncIOScheduler()

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Bot started. Send videos to the group to queue them for posting.")

@dp.message(F.video)
async def handle_video(message: types.Message):
    if message.chat.id == GROUP_ID:
        video = message.video
        file_id = video.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        files = os.listdir(SAVE_DIR)
        video_count = len(files)

        video_name = f"{message.message_id}_video.mp4"
        video_path = os.path.join(SAVE_DIR, video_name)

        await bot.download_file(file_path, video_path)
        
        await message.answer(f"Видео добавлено в очередь как {video_name} \n Позиция в очереди: {video_count + 1}")

async def send_videos_to_channel():
    files = os.listdir(SAVE_DIR)
    if not files:
        await bot.send_message(chat_id=GROUP_ID, text='В очереди нет видео для отправки')
        return

    for file_name in files:
        video_path = os.path.join(SAVE_DIR, file_name)
        if os.path.isfile(video_path):
            try:
                video = FSInputFile(video_path)
                await bot.send_video(chat_id=CHANNEL_ID, video=video)
                os.remove(video_path)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Ошибка при отправке видео {file_name}: {e}")

@dp.message(Command("clear"))
async def clear_command(message: types.Message):
    files = os.listdir(SAVE_DIR)
    if files:
        last_file = files[-1]
        file_path = os.path.join(SAVE_DIR, last_file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        await message.answer("Последнее видео удалено")
    else:
        await message.answer("Очередь пуста")

@dp.message(Command("queue"))
async def queue_command(message: types.Message):
    files = os.listdir(SAVE_DIR)
    video_count = len(files)
    await message.answer(f"В очереди на отправку {video_count} видео.")

async def on_startup():
    await bot.send_message(chat_id=GROUP_ID, text='Бот запущен, отправляйте видео')

async def on_shutdown():
    await bot.send_message(chat_id=GROUP_ID, text='Бот остановлен')

def schedule_jobs():
    
    scheduler.add_job(send_videos_to_channel, 'cron', hour=10, minute=0)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=12, minute=0)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=14, minute=0)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=16, minute=0)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=18, minute=0)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=20, minute=0)

    scheduler.start()

async def main():
    schedule_jobs()
    await dp.start_polling(bot, on_startup=on_startup(), on_shutdown=on_shutdown())

if __name__ == '__main__':
   print("IM ALIVE")
   asyncio.run(main())
   
