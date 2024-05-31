from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo, Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
import functools
from Loggs import logger


'''
Декоратор для отлова ошибок
'''
def error_handler(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        message_or_call = next((arg for arg in args if isinstance(arg, (Message, CallbackQuery))), None)
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            username = (message_or_call.from_user.username 
                        if message_or_call and isinstance(message_or_call, (Message, CallbackQuery)) 
                        else 'Unknown user')
            logger.debug(f'У пользователя {username} возникла ошибка при выполнении функции "{func.__name__}": {e}')
            
            if message_or_call:
                error_message = "Кажется, что произошла ошибка 😨\n\nОбязательно напиши об этом @Megagigapoopfart"
                if isinstance(message_or_call, Message):
                    await message_or_call.answer(error_message, reply_markup=button(["Главное меню"]))
                elif isinstance(message_or_call, CallbackQuery):
                    await message_or_call.message.edit_text(error_message, reply_markup=button(["Главное меню"]))
    return wrapper


'''
Клавиатура главного меню
'''
StartKB = InlineKeyboardBuilder()
buttons_list = ["Добавить слово в свой словарь", "Учить свои слова", "Учить по темам", "Добавить слова по темам", "Рейтинговая игра"]

for i in buttons_list:
    StartKB.button(text=i, callback_data=i)
StartKB.adjust(1, 2, 1, 1,)


'''
Функция для созданяи inline-клавиатуры
'''
def button(text : list):
    KB = InlineKeyboardBuilder()
    for i in text:
        KB.button(text=i, callback_data=i)
    KB.adjust(1,)
    return KB.as_markup()


'''
Функция для создания клавиатуры с темами
'''
def themes_button(text : list):
    KB = InlineKeyboardBuilder()
    for i in text:
        KB.button(text=i, callback_data=f"theme_{i}")
    KB.adjust(1,)
    return KB.as_markup


'''
Кнопка для перехода на pealim.com
'''
pealimKB = InlineKeyboardBuilder()
pealimKB.button(
    text="Перейти", web_app=WebAppInfo(url="https://www.pealim.com/ru/search/")
)
pealimKB.adjust(1,)


'''
Настройка пагинации (все ниже)
Я просто хз как эта хуйня работает это просто копипаста
'''
class Pagination(CallbackData, prefix="pag"):
    action: str  # Действие
    page: int  # Номер страницы

class Pagination2(CallbackData, prefix="page"):
    action: str  # Действие
    page: int  # Номер страницы

async def paginator(themes : list, page: int = 0, ):
    builder = InlineKeyboardBuilder() 

    start_offset = page * 3  # Вычисление начального смещения на основе номера страницы
    limit = 3  # Определение лимита тем на одной странице
    end_offset = start_offset + limit  # Вычисление конечного смещения

    for theme in themes[start_offset:end_offset]:  
        builder.button(text=theme ,callback_data=f"theme_{theme}")  # Добавление кнопки для каждой темы
    buttons_row = []  
    if page > 0:  
        buttons_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=Pagination(action="prev", page=page - 1).pack()))  # Добавление кнопки "назад"
    if end_offset < len(themes):  
        buttons_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=Pagination(action="next", page=page + 1).pack()))  # Добавление кнопки "вперед"
    
    builder.row(*buttons_row)  
    builder.adjust(1,)
    return builder.as_markup()  



async def paginator_for_themed_learn(themes : list, page: int = 0):
    builder = InlineKeyboardBuilder() 

    start_offset = page * 3  # Вычисление начального смещения на основе номера страницы
    limit = 3  # Определение лимита тем на одной странице
    end_offset = start_offset + limit  # Вычисление конечного смещения

    for theme in themes[start_offset:end_offset]:  
        builder.button(text=theme ,callback_data=f"learn_themed_{theme}")  # Добавление кнопки для каждой темы
    buttons_row = []  
    if page > 0:  
        buttons_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=Pagination2(action="prev", page=page - 1).pack()))  # Добавление кнопки "назад"
    if end_offset < len(themes):  
        buttons_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=Pagination2(action="next", page=page + 1).pack()))  # Добавление кнопки "вперед"
    
    builder.row(*buttons_row)  
    builder.adjust(1,)
    return builder.as_markup()  


