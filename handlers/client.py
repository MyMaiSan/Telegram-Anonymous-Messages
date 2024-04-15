from aiogram import Bot, F, types, Router, Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.utils import deep_linking
from config import BOT_USERNAME, ADMINS_ID
from filters.filters import DeepLinkFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.kb import again_kb, admin_kb
from time import time
from database.db import DB




client = Router()
dp = Dispatcher()

class AnonStates(StatesGroup):
    get_message = State()
    send_again = State()
    send_text = State()
    answer_state = State()


@client.message(CommandStart(), DeepLinkFilter())
async def deep_start(message: types.Message, state: FSMContext):
    await DB.add_user(message.from_user.id)
    await state.set_state(AnonStates.get_message)
    payload = message.text.split()[1]
    start_time = time()
    await state.update_data(time=None)
    await state.update_data(to_send=payload)

    await message.answer("""
🚀 Здесь можно отправить анонимное сообщение человеку, который опубликовал эту ссылку.

Напишите сюда всё, что хотите ему передать и через несколько секунд он получит ваше сообщение, но не будет знать от кого.

Отправить можно фото, видео, текст, голосовые, видеосообщения (кружки), а также стикеры.

⚠️ Это полностью анонимно!""")

    await state.set_state(AnonStates.get_message)

@client.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await DB.add_user(message.from_user.id)
    await state.clear()
    
    link = deep_linking.create_deep_link(username=BOT_USERNAME, 
    link_type='start', payload=str(message.from_user.id))
    
    
    photo_file = types.FSInputFile(path='./files/welcome.jpg')
    text = f"""
🚀 Начни получать анонимные сообщения прямо сейчас!

Твоя личная ссылка:

🔗 <code>{link}</code>

Размести эту ссылку в своём профиле Telegram/Instagram/TikTok или других соц сетях, чтобы начать получать сообщения"""
    await message.answer_photo(photo=photo_file, caption=text, parse_mode='html')
    

@client.message(AnonStates.get_message, F.text)
async def get_message(message: types.Message, state: FSMContext, bot: Bot):

    payload = await state.get_data()
    start_time = await state.get_data()
    start_time = start_time['time']
    photo_file = types.FSInputFile('./files/new_message.jpg')
    photo_file_answer = types.FSInputFile('./files/answer_sended.jpg')
    text = f"""
<b>У тебя новое сообщение!</b>

{message.text}

↩️<i>Свайпни для ответа</i>"""
    cur_time = time()
    
    if start_time:
        if (cur_time - start_time) >= 60:
            await message.answer_photo(photo=photo_file_answer, reply_markup=again_kb())
            await state.update_data(time=start_time)
            await bot.send_photo(photo=photo_file, chat_id=payload['to_send'], caption=text,  parse_mode='HTML')
            await state.set_state(AnonStates.send_again)
            cur_time = time()
            await state.update_data(time=cur_time)
            
        else:
            await message.answer('Не так часто!')
    else:
        cur_time = time()
        await state.update_data(time=cur_time)
        await message.answer_photo(photo=photo_file_answer, reply_markup=again_kb())
        await bot.send_photo(photo=photo_file, chat_id=payload['to_send'], caption=text,  parse_mode='HTML')
        await state.set_state(AnonStates.send_again)
    
    cur_state = dp.fsm.get_context(bot=bot, chat_id=int(payload['to_send']), user_id=int(payload['to_send']))
    await cur_state.update_data(userid=message.from_user.id)
    await cur_state.update_data(messageid=message.message_id)
    await cur_state.set_state(AnonStates.answer_state)
    

@client.message(AnonStates.get_message)
async def get_message_other(message: types.Message, state: FSMContext, bot: Bot):
    payload = await state.get_data()
   
    photo_file = types.FSInputFile('./files/new_message.jpg')
    
    text = f"""
<b>У тебя новое сообщение!</b>


↩️<i>Свайпни для ответа</i>"""
    await bot.send_photo(photo=photo_file, chat_id=payload['to_send'], caption=text,  parse_mode='HTML')
    await bot.copy_message(chat_id=payload['to_send'], from_chat_id=message.chat.id,
                           message_id=message.message_id)

    cur_state = dp.fsm.get_context(bot=bot, chat_id=payload['to_send'], user_id=payload['to_send'])
    await cur_state.update_data(userid=message.from_user.id)
    await cur_state.update_data(messageid=message.message_id)
    await cur_state.set_state(AnonStates.answer_state)
    

    
@client.callback_query(F.data == 'send_again')
async def send_again(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    
    payload = await state.get_data()
    start_time = await state.get_data()
    start_time = start_time['time']
    
    cur_time = time()
    
    if start_time:
        if (cur_time - start_time) >= 60:
            await callback.message.answer('Отправьте сообщение')
            cur_time = time()
            await state.update_data(time=cur_time)
            await state.set_state(AnonStates.send_text)
            await callback.answer()
        else:
            await callback.answer('Не так часто!')
    else:
        cur_time = time()
        await state.update_data(time=cur_time)
        await callback.message.answer('Отправьте сообщение')
        await state.set_state(AnonStates.send_text)
        await callback.answer()
        
    
@client.message(AnonStates.send_text, F.text)
async def send_again(message: types.Message, state: FSMContext, bot: Bot):
    payload = await state.get_data()
    
    photo_file = types.FSInputFile('./files/new_message.jpg')
    photo_file_answer = types.FSInputFile('./files/answer_sended.jpg')
    
    start_time = await state.get_data()
    start_time = start_time['time']
    
    text = f"""
<b>У тебя новое сообщение!</b>

{message.text}

↩️<i>Свайпни для ответа</i>"""
    
    await message.answer_photo(photo=photo_file_answer, reply_markup=again_kb())
    await bot.send_photo(photo=photo_file, chat_id=payload['to_send'], caption=text,  parse_mode='HTML')
    cur_time = time()
    cur_state = dp.fsm.get_context(bot=bot, chat_id=int(payload['to_send']), user_id=int(payload['to_send']))
    await cur_state.update_data(userid=message.from_user.id)
    await cur_state.update_data(messageid=message.message_id)
    await cur_state.set_state(AnonStates.answer_state)
    await state.update_data(time=cur_time)
    

    
@client.message(AnonStates.send_text)
async def send_again_other(message: types.Message, state: FSMContext, bot: Bot):
    payload = await state.get_data()
   
    photo_file = types.FSInputFile('./files/new_message.jpg')
    text = f"""
<b>У тебя новое сообщение!</b>

↩️<i>Свайпни для ответа</i>"""
    await bot.send_photo(photo=photo_file, chat_id=payload['to_send'], caption=text,  parse_mode='HTML')
    await bot.copy_message(chat_id=payload['to_send'], from_chat_id=message.chat.id,
                           message_id=message.message_id)
    cur_state = dp.fsm.get_context(bot=bot, chat_id=int(payload['to_send']), user_id=int(payload['to_send']))
    await cur_state.update_data(userid=message.from_user.id)
    await cur_state.update_data(messageid=message.message_id)
    await cur_state.set_state(AnonStates.answer_state)
    

@client.message(AnonStates.answer_state)
async def answer_state_handler(message: types.Message, bot: Bot, state: FSMContext):
    if message.reply_to_message:
        data = await state.get_data()
        userid = data['userid']
        messageid = data['messageid']
        
        await bot.send_message(chat_id=userid, text=message.text, reply_to_message_id=messageid, reply_markup=again_kb())
        await state.clear()
    
    