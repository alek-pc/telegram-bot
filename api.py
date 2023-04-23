from telegram import ReplyKeyboardMarkup
import aiohttp
from constants import PAYLOADS, URLS, GPT_HEADERS, MARKUPS
import datetime
from data.db_session import create_session
from data.users import User


# раздел api
async def gpt(update, context):
    db_sess = create_session()
    user = db_sess.query(User).filter(User.user_id == int(update.effective_user.id)).first()
    user.last_visit = datetime.datetime.now()
    db_sess.commit()
    context.user_data['mode'] = 'gpt'
    await update.message.reply_text('Вы перешли в раздел gpt',
                                    reply_markup=ReplyKeyboardMarkup([*MARKUPS['gpt']], one_time_keyboard=False,
                                                                     resize_keyboard=True))


# начало диалога с api
async def dialog(update, context):
    await update.message.reply_text('Начнем диалог (долго), если надоело, нажмите /stop, а сейчас начните',
                                    reply_markup=ReplyKeyboardMarkup([['/stop']], one_time_keyboard=False,
                                                                     resize_keyboard=True))
    return 'dialog'


# сам диалог
async def processing(update, context):
    PAYLOADS['text']['messages'][0]['content'] = update.message.text
    async with aiohttp.ClientSession() as session:
        async with session.request('POST', URLS['text'], headers=GPT_HEADERS, json=PAYLOADS['text']) as resp:
            resp = await resp.json()
            await update.message.reply_text(resp['choices'][0]['message']['content'])
    return 'dialog'


# начало генерации изображения
async def image(update, context):
    await update.message.reply_text('Генерация картинки (долго). Введите описание картинки или /stop',
                                    reply_markup=ReplyKeyboardMarkup([['/stop']], one_time_keyboard=False,
                                                                     resize_keyboard=True))
    return 'generation'


# генерация изображения
async def generation(update, context):
    PAYLOADS['images']['prompt'] = update.message.text
    async with aiohttp.ClientSession() as session:
        async with session.request('POST', URLS['images'], headers=GPT_HEADERS, json=PAYLOADS['images']) as resp:
            resp = await resp.json()
            await context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=resp['data'][0]['url'],
                caption=f"Ну как?"
            )
    await update.message.reply_text('Дальше?')
    return 'generation'
