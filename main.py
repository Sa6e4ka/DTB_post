import os
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio

API_TOKEN = '7388500114:AAG2UqsO8avMrAsyOkkLSnhS332nJpV-whE'
GROUP_ID = -4578892217  
SAVE_DIR = "videos" 
CHANNEL_ID = '@daun_type_beat'  

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
print(os.listdir(SAVE_DIR))

@dp.message_handler(content_types=types.ContentType.VIDEO, chat_id=GROUP_ID)
async def handle_video(message: types.Message):
    video = message.video
    file_id = video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    files = os.listdir(SAVE_DIR)
    video_count = len(files)

    video_name = f"{message.message_id}_video.mp4"
    video_path = os.path.join(SAVE_DIR, video_name)

    await bot.download_file(file_path, video_path)
    
    await message.reply(f"Видео добавлено в очередь как {video_name} \n Позиция в очереди: {video_count + 1}")

async def send_videos_to_channel():
    flag = True
    files = os.listdir(SAVE_DIR)
    if not files:
        await bot.send_message(chat_id=GROUP_ID, text='В очереди нет видео для отправки')
        flag = False

    if flag:
        for file_name in files:
            video_path = os.path.join(SAVE_DIR, file_name)
            if os.path.isfile(video_path):
                try:
                    with open(video_path, 'rb') as video:
                        await bot.send_video(chat_id=CHANNEL_ID, video=video)
                    os.remove(video_path)
                    await asyncio.sleep(1)  
                    print('Видео загружено успешно')
                except Exception as e:
                    print(f"Ошибка при отправке видео {file_name}: {e}")
        


@dp.message_handler(commands=['clear'])
async def clear_command(message: types.Message):
    files = os.listdir(SAVE_DIR)
    for file_name in files[::-1]:
        file_path = os.path.join(SAVE_DIR, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        break
    await message.reply("Последнее видео удалено")



@dp.message_handler(commands=['queue'])
async def queue_command(message: types.Message):
    files = os.listdir(SAVE_DIR)
    video_count = len(files)
    await message.reply(f"В очереди на отправку {video_count} видео.")

async def on_startup(dp):
    await bot.send_message(chat_id=GROUP_ID, text='Бот запущен, отправляйте видео')

async def on_shutdown(dp):
    await bot.send_message(chat_id=GROUP_ID, text='Бот остановлен')

def schedule_jobs():
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(send_videos_to_channel, 'cron', hour=0, minute=28)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=0, minute=30)
    scheduler.add_job(send_videos_to_channel, 'cron', hour=0, minute=32)

    
    scheduler.start()

if __name__ == '__main__':
    schedule_jobs()

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)

