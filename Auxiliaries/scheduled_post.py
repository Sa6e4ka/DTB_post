from os import environ
from dotenv import load_dotenv
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger 
from aiogram import Bot

from Loggs import logger

load_dotenv()
scheduler = AsyncIOScheduler()

async def schedule_post(file: str, bot: Bot, timeslot: int, global_state: dict) -> None:
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
            chat_id=environ.get("CHANEL_NAME"),  # ID вашего канала
            video=file
        )

        if "videos" in global_state and file in global_state["videos"]:
            global_state["videos"].remove(file)

            logger.info(f"Видео {file} успешно отправилось и удаленно из очереди")

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
    
    # Проверяем, есть ли уже задача на отправку этого видео
    job_id = f"send_video_{file}_{scheduled_time.timestamp()}"
    existing_job = scheduler.get_job(job_id)

    if not existing_job:
        # Добавляем задачу в планировщик с уникальным идентификатором
        scheduler.add_job(
            send_videos, 
            trigger=CronTrigger(
                year=scheduled_time.year, 
                month=scheduled_time.month, 
                day=scheduled_time.day, 
                hour=scheduled_time.hour, 
                minute=scheduled_time.minute, 
                second=scheduled_time.second
            ), 
            id=job_id
        )
    
    logger.info(f"Отправка видео {job_id} запланировано на: {scheduled_time}")
    return scheduled_time
