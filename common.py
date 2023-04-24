from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup
from data.users import User
from data.timers import Timer
from data.lists import List
from data.db_session import create_session
from timers import task
from constants import HELP, MARKUPS
from server import logger
import datetime


# помощь
async def help(update, context):
    if not context.args:
        await update.message.reply_text(f"""Подъехала помощь!
{HELP['base']}
Доступные разделы:
{HELP['help']}

{HELP['timers']}

{HELP['lists']}

{HELP['gpt']}
""")
    else:
        text = "\n".join([HELP[i] for i in context.args])
        await update.message.reply_text(f'Подъехала помощь!\n{text}')


# старт
async def start(update, context):
    context.user_data['mode'] = 'base'  # режим главной страницы
    db_sess = create_session()
    # если юзера еще нет в бд - добавляем его
    if not list(db_sess.query(User).filter(User.user_id == update.effective_user.id)):
        logger.debug('new user was added')
        user = User()
        user.user_id = update.effective_user.id
        user.name = update.effective_user.name
        db_sess.add(user)
        db_sess.commit()
    markup = ReplyKeyboardMarkup(MARKUPS['base'], one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(f'Здравствуйте, я - телеграм бот (как будто не понятно) помощник в быту, '
                                    f'для объяснений вызовите команду /help', reply_markup=markup)


# ввод обычного текста: старт таймера, выбор списка
async def text(update, context):
    db_sess = create_session()
    if 'mode' not in list(context.user_data.keys()) or context.user_data['mode'] == 'timers':
        timer = db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id,
                                            Timer.name == update.message.text).first()
        if not timer:
            await update.message.reply_text('Что за бред? На клавиатуре есть доступные таймеры, куда жмете?!')
            return
        chat_id = update.effective_message.chat_id
        context.job_queue.run_once(task, timer.seconds + timer.minutes * 60 + timer.hours * 3600, chat_id=chat_id,
                                   name=str(chat_id), data=f'Таймер {timer.name} истек')
        await update.message.reply_text(f'Таймер {timer.name} на {timer.hours} ч '
                                        f'{timer.minutes} мин {timer.seconds} сек поставлен')
    elif context.user_data['mode'] == 'lists':  # раздел списков - запоминаем его имя для функций, связанных с ним
        context.user_data['list name'] = update.message.text
        context.user_data['mode'] = 'concrete list'
        await update.message.reply_text(f'Вы перешли в список {update.message.text}',
                                        reply_markup=ReplyKeyboardMarkup([*MARKUPS['concrete list']],
                                                                         resize_keyboard=True))
    user = db_sess.query(User).filter(User.user_id == int(update.effective_user.id)).first()
    user.last_visit = datetime.datetime.now()
    db_sess.commit()


# назад
async def back(update, context):
    markup = None
    db_sess = create_session()
    if 'mode' not in list(context.user_data.keys()) or context.user_data['mode'] in 'timers lists gpt':
        context.user_data['mode'] = 'base'
        markup = ReplyKeyboardMarkup(MARKUPS['base'], one_time_keyboard=False, resize_keyboard=True)
    elif context.user_data['mode'] == 'concrete list':
        context.user_data['mode'] = 'lists'
        personal_lists = [el.name for el in db_sess.query(List).all() if str(update.effective_user.id) in
                          el.members.split(';')]
        markup = ReplyKeyboardMarkup([*MARKUPS['lists'], personal_lists], one_time_keyboard=False, resize_keyboard=True)

    user = db_sess.query(User).filter(User.user_id == int(update.effective_user.id)).first()
    user.last_visit = datetime.datetime.now()
    db_sess.commit()

    await update.message.reply_text('Вернулись', reply_markup=markup)


# стоп conversationHandler
async def stop(update, context):
    db_sess = create_session()
    markup = None
    if context.user_data['mode'] == 'timers':
        timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
        user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
        markup = ReplyKeyboardMarkup([*MARKUPS['timers'], *user_timers], one_time_keyboard=False, resize_keyboard=True)
    elif context.user_data['mode'] == 'lists':
        personal_lists = [el.name for el in db_sess.query(List).all() if str(update.effective_user.id) in
                          el.members.split(';')]
        markup = ReplyKeyboardMarkup([*MARKUPS['lists'], personal_lists], one_time_keyboard=False, resize_keyboard=True)
    elif context.user_data['mode'] == 'concrete list':
        markup = ReplyKeyboardMarkup([*MARKUPS['concrete list']], one_time_keyboard=False, resize_keyboard=True)
    elif context.user_data['mode'] == 'gpt':
        markup = ReplyKeyboardMarkup([*MARKUPS['gpt']], one_time_keyboard=False, resize_keyboard=True)

    user = db_sess.query(User).filter(User.user_id == int(update.effective_user.id)).first()
    user.last_visit = datetime.datetime.now()
    db_sess.commit()
    await update.message.reply_text('Вышли', reply_markup=markup)
    return ConversationHandler.END
