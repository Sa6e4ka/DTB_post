'''
Отправка логов по команде
'''
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from dotenv import load_dotenv
from os import environ

from Auxiliaries import button
from Loggs import error_handler_func

load_dotenv()

#Logging Router
logging_router = Router() 


'''
Обработчик команды для отправки логов
'''
@logging_router.message(Command("loggs"))
@error_handler_func
async def send_to_channel(message: Message, bot: Bot):
    file_info = FSInputFile("Loggs/loggs.log")

    await bot.send_document(
        chat_id=environ.get("CHAT_ID"), 
        document=file_info, caption="Последние логи"
    )



