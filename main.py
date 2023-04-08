import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from data.db_session import global_init, create_session
from data.users import User
from data.timers import Timer
from timers import *
from constants import BOT_TOKEN

# ссылка на бота в телеграм https://t.me/asdfagsfbot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

global_init('db/telegram-bot.db')


async def help(update, context):
    if not context.args:
        await update.message.reply_text(f"""Подъехала помощь!
{HELP['base']}
Доступные разделы:
{HELP['help']}
{HELP['timer']}
""")
    else:
        await update.message.reply_text(f'Подъехала помощь!\n{"   ".join([HELP[i] for i in context.args])}')


async def start(update, context):
    context.user_data['mode'] = 'base'  # режим главной страницы
    db_sess = create_session()
    # если юзера еще нет в бд - добавляем его
    if not list(db_sess.query(User).filter(User.name == update.effective_user.id)):
        logger.debug('new user was added')
        user = User()
        user.name = update.effective_user.id
        db_sess.add(user)
        db_sess.commit()

    markup = ReplyKeyboardMarkup(MARKUPS['base'], one_time_keyboard=False)
    await update.message.reply_text(f'Здравствуйте, я - телеграм бот (как будто не понятно) помощник в быту, '
                                    f'для объяснений вызовите команду /help', reply_markup=markup)


async def text(update, context):
    if context.user_data['mode'] == 'timer':
        db_sess = create_session()
        timer = db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id,
                                            Timer.name == update.message.text).first()
        if not timer:
            await update.message.reply_text('Что за бред? На клавиатуре есть доступные таймеры, куда жмете?!')
            return
        chat_id = update.effective_message.chat_id
        context.job_queue.run_once(task, timer.seconds + timer.minutes * 60 + timer.hours * 3600 +
                                   timer.days * 3600 * 24, chat_id=chat_id,
                                   name=str(chat_id), data=f'Таймер {timer.name} истек')
        await update.message.reply_text(f'Таймер {timer.name} поставлен')


async def back(update, context):
    if context.user_data['mode'] == 'timer':
        context.user_data['mode'] = 'base'
        markup = ReplyKeyboardMarkup(MARKUPS['base'], one_time_keyboard=False)
        await update.message.reply_text('Вернулись', reply_markup=markup)


async def stop(update, context):
    await update.message.reply_text('Вышли')
    return ConversationHandler.END


async def edit_timer2(update, context):
    await update.message.reply_text('Какой таймер будем редактировать? Введите имя')
    return 'get name'


async def get_edit_timer_name(update, context):
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.name == update.message.text,
                                        Timer.user_id == update.effective_user.id).first()
    if not timer:
        await update.message.reply_text('Такого таймера не существует. Введите имя таймера или выйдите /stop')
        return 'get name'
    context.user_data['edit timer conv'] = update.message.text
    await update.message.reply_text('Введите новое имя таймера (если нет, то "нет")',
                                    reply_markup=ReplyKeyboardMarkup([['нет']], one_time_keyboard=True))
    return 'new name'


async def new_timer_name(update, context):
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.name == context.user_data['edit timer conv'],
                                        Timer.user_id == update.effective_user.id).first()
    if update.message.text.lower() != 'нет':
        if db_sess.query(Timer).filter(Timer.name == update.message.text,
                                       Timer.user_id == update.effective_user.id).first():
            await update.message.reply_text('Это имя уже используется, выберите другое или напишите "нет"')
            return 'new name'
        timer.name = update.message.text
        context.user_data['edit timer conv'] = timer.name

    await update.message.reply_text('Теперь введите новое время для таймера')
    return 'get time'


async def get_edit_timer_time(update, context):
    if any([i not in '123456789 ' for i in update.message.text]) or len(update.message.text.split()) > 4:
        await update.message.reply_text('Некорректное время, введите время ещё раз')
        return 'get time'
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.name == context.user_data['edit timer conv'],
                                        Timer.user_id == update.effective_user.id).first()

    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(update.message.text.split()):
        time[ind] = int(el)
    timer.seconds = time[0]
    timer.minutes = time[1]
    timer.hours = time[2]
    timer.days = time[3]
    db_sess.commit()

    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)

    await update.message.reply_text(f'Окей. Теперь таймер {timer.name} установлен на {timer.days} дней {timer.hours} ч '
                                    f'{timer.minutes} мин {timer.seconds} сек', reply_markup=markup)
    return ConversationHandler.END


async def add_timer2(update, context):
    await update.message.reply_text('Создаем новый таймер. Введите имя нового таймера')
    return 'get name'


async def get_add_timer_name(update, context):
    db_sess = create_session()
    if db_sess.query(Timer).filter(Timer.name == update.message.text,
                                   Timer.user_id == update.effective_user.id).first():
        await update.message.reply_text(f'Таймер {update.message.text} уже существует, выберите другое имя')
        return 'get name'
    context.user_data['add timer conv'] = update.message.text
    await update.message.reply_text(f'Введите время таймера {update.message.text}')
    return 'get time'


async def get_add_timer_time(update, context):
    if any([i not in '123456789 ' for i in update.message.text]) or len(update.message.text.split()) > 4:
        await update.message.reply_text('Некорректное время, введите время ещё раз')
        return 'get time'
    db_sess = create_session()
    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(update.message.text.split()):
        time[ind] = int(el)
    timer = Timer(name=context.user_data['add timer conv'], seconds=time[0], minutes=time[1], hours=time[2],
                  days=time[3], user_id=update.effective_user.id)
    db_sess.add(timer)
    db_sess.commit()
    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Создан новый таймер {timer.name}', reply_markup=markup)
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))

    application.add_handler(CommandHandler('timer', timers))

    application.add_handler(CommandHandler('set_timer', set_timer))
    application.add_handler(CommandHandler('add_timer', add_timer))
    application.add_handler(CommandHandler('edit_timer', edit_timer))
    application.add_handler(CommandHandler('delete_timer', delete_timer))
    application.add_handler(CommandHandler('back', back))

    application.add_handler(ConversationHandler(entry_points=[CommandHandler('edit_timer2', edit_timer2)], states={
        'get name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_timer_name)],
        'new name': [MessageHandler(filters.TEXT & ~filters.COMMAND, new_timer_name)],
        'get time': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_timer_time)],
    }, fallbacks=[CommandHandler('stop', stop)]))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('add_timer2', add_timer2)], states={
        'get name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_timer_name)],
        'get time': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_timer_time)]
    }, fallbacks=[CommandHandler('stop', stop)]))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    application.run_polling()


if __name__ == '__main__':
    main()
