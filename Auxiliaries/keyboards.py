from aiogram.utils.keyboard import InlineKeyboardBuilder

'''
Функция для созданяи inline-клавиатуры
'''
def button(text : list):
    KB = InlineKeyboardBuilder()
    for i in text:
        KB.button(text=i, callback_data=i)
    KB.adjust(1,)
    return KB.as_markup()