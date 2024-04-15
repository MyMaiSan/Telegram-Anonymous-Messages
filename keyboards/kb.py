from aiogram.utils.keyboard import InlineKeyboardBuilder


again = InlineKeyboardBuilder()

def again_kb():
    
    ikb = InlineKeyboardBuilder()
    ikb.button(text='🔄Написать ещё', callback_data='send_again')
    
    return ikb.as_markup()

def admin_kb():
    ikb = InlineKeyboardBuilder()
    
    ikb.button(text='Статистика📊', callback_data='stats')
    ikb.button(text='Выгрузка📝', callback_data='upload')
    ikb.button(text='Рассылка📩', callback_data='mailing')
    
    ikb.adjust(1,2)
    
    return ikb.as_markup()