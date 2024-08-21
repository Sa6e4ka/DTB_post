import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger 
from aiogram import Bot

load_dotenv()
CHANNEL_ID= os.environ.get("CHANNEL_ID")

scheduler = AsyncIOScheduler()

async def schedule_post(file: str, bot: Bot, timeslot: int) -> None:
    '''
    Отложенная отправка видео
    :param file: id видео с сервера tg
    :param bot: экземпляр класса Bot aiogram 
    '''
    async def send_videos():
        '''
        Отправка видео в канал
        '''
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=file
        )

    # Рассчитываем час на основе timeslot
    days_ahead = timeslot // 6
    slot_in_day = timeslot % 6
    hour = 10 + slot_in_day * 2

    now = datetime.now()
    scheduled_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    # Если текущее время позже запланированного, переносим на следующий день
    if now >= scheduled_time:
        days_ahead += 1

    scheduled_time += timedelta(days=days_ahead)
    
    # Добавляем задачу в планировщик
    scheduler.add_job(send_videos, trigger=CronTrigger(year=scheduled_time.year, month=scheduled_time.month, day=scheduled_time.day, hour=scheduled_time.hour, minute=scheduled_time.minute))

    return scheduled_time