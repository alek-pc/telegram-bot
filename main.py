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

    markup = ReplyKeyboardMarkup(MARKUPS['base'], one_time_keyboard=True)
    await update.message.reply_text(f'Здравствуйте, я - телеграм бот (как будто не понятно) помощник в быту, '
                                    f'для объяснений вызовите команду /help', reply_markup=markup)


async def commands(update, context):
    if context.user_data['mode'] == 'timer':
        db_sess = create_session()
        timer = db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id,
                                            Timer.command == update.message.text).first()
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


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))

    application.add_handler(CommandHandler('timer', timer))  #

    application.add_handler(CommandHandler('set_timer', set_timer))
    application.add_handler(CommandHandler('add_timer', add_timer))
    application.add_handler(CommandHandler('edit_timer', edit_timer))
    application.add_handler(CommandHandler('delete_timer', delete_timer))
    application.add_handler(CommandHandler('back', back))
    application.add_handler(MessageHandler(filters.TEXT, commands))

    application.run_polling()


if __name__ == '__main__':
    main()
