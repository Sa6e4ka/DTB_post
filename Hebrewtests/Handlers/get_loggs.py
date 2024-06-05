'''
Отправка логов по команде
'''
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import  Message, FSInputFile
from Auxiliaries import button, error_handler


#Logging Router
logging_router = Router() 


'''
Обработчик команды для отправки логов
'''
@logging_router.message(Command("loggs"))
@error_handler
async def send_to_channel(message: Message):
      file_info = FSInputFile("loggs/debug.log")
      await message.answer_document(document=file_info, caption="Последние логи", reply_markup=button(["Главное меню"]))




