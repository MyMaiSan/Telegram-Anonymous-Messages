from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.kb import admin_kb
from database.db import DB
from aiogram.exceptions import TelegramForbiddenError
from config import ADMINS_ID
import os

class MailingStates(StatesGroup):
    message = State()

admin = Router()


@admin.callback_query(F.data == 'stats')
async def stats_handler(callback: types.CallbackQuery):
    
    user_count = len(await DB.select_all())
    
    text = f"""
    Статистка
    
Всего юзеров: {user_count}"""

    await callback.message.answer(text)
    await callback.answer()
    
    
@admin.callback_query(F.data == 'upload')
async def upload_handler(callback: types.CallbackQuery, bot: Bot):
    users = await DB.select_all()
    
    with open('users.txt', 'w') as file:
        for user in users:
            file.write(f"{user['user_id']}\n")
        
    input_file = types.FSInputFile('users.txt')
            
    await bot.send_document(chat_id=callback.from_user.id, document=input_file)
    os.remove('./users.txt')
    await callback.answer()
    
    
@admin.callback_query(F.data == 'mailing')
async def mailing_handler(callback: types.CallbackQuery, state: FSMContext):
    
    await callback.message.answer('Отправьте сообщение для рассылки')
    await state.set_state(MailingStates.message)
    await callback.answer()
    
    
@admin.message(MailingStates.message)
async def mailing_get_msg(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text
    users = await DB.select_all()
    
    for user in users:
        try:
            await bot.copy_message(chat_id=int(user['user_id']), from_chat_id=message.from_user.id, message_id=message.message_id)
        except TelegramForbiddenError:
            await DB.delete_user(user['user_id'])
        
    await message.answer('Рассылка закончена!')
    await state.clear()
    
@admin.message(F.text.lower() == '/admin')
async def admin_cmd(message: types.Message):
    if message.from_user.id in ADMINS_ID:
        await message.answer('Добро пожаловать', reply_markup=admin_kb())