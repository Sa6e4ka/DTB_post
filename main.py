# Импортируем нужные дополнительные модули
import os
import asyncio
from Loggs import logger

# Импортируем нужные модули из aiogram
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import BotCommandScopeAllPrivateChats, Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties


# Достаем токен бота и url базы данных из переменной окружения
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


# Из папки handlers импортируем все хендлеры
from Handlers import (router_, scheduler)

# Импортируем команды
from Auxiliaries import private

TOKEN = str(os.environ.get("TOKEN"))
# Создаем объект бота (передаем ему режим парсига получаемых ответов)
bot = Bot(token="6851613825:AAGlWJ7uueyif8JcmAFRlXtg-7ihNN0J_d8", default=DefaultBotProperties(parse_mode='HTML'))
# Создаем объект диспетчера
dp = Dispatcher()

# Подключаем к диспетчеру все роутеры из создаваемых хендлеров
dp.include_routers(router_,)


# Добавляем основные "глобальные" хендлеры
@dp.message(Command('state'))
async def state_get(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(text=f'Текущее состояние: {current_state}')


@dp.message(Command('stateclear'))
async def clear_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await state.clear()
    clear_state = await state.get_state()
    await message.answer(f'Состояние <b>{current_state}</b> сменилось на <b>{clear_state}</b>')


# Запускаем бота, помещаем доступные апдейты в start_polling
# отключаем обработку незавершившихся запросов
async def main():
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

# Запуск main
if __name__ == "__main__":
    try:
        logger.info(f"Бот запущен по ссылке {os.environ.get("BOT_LINK")}")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот остановлен!')
        pass
    except Exception as e:
        logger.error(f'CRITICAL ERROR: {e}')