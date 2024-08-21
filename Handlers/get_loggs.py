'''
Отправка логов по команде
'''
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import  Message, FSInputFile, CallbackQuery
from Auxiliaries import button
from Loggs import error_handler_func

#Logging Router
logging_router = Router() 

'''
Обработчик команды для отправки логов
'''
@logging_router.message(Command("loggs"))
@error_handler_func
async def send_to_channel(message: Message):
      file_info = FSInputFile("loggs/debug.log")
      await message.answer_document(document=file_info, caption="Последние логи", reply_markup=button(["Главное меню"]))



