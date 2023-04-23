import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from data.db_session import global_init
from timers import *
from lists import *
from constants import BOT_TOKEN
from common import *
from api import *

# ссылка на бота в телеграм https://t.me/asdfagsfbot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

global_init('db/telegram-bot.db')


# установка всех хэндлеров
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))

    application.add_handler(CommandHandler('timers', timers))

    application.add_handler(CommandHandler('set_timer', set_timer))
    application.add_handler(CommandHandler('back', back))
    stop_comm = CommandHandler('stop', stop)

    application.add_handler(ConversationHandler(entry_points=[CommandHandler('edit_timer', edit_timer)], states={
        'get name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_timer_name)],
        'new name': [MessageHandler(filters.TEXT & ~filters.COMMAND, new_timer_name)],
        'get time': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_timer_time)],
    }, fallbacks=[stop_comm]))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('add_timer', add_timer)], states={
        'get name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_timer_name)],
        'get time': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_add_timer_time)]
    }, fallbacks=[stop_comm]))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('delete_timer', delete_timer)], states={
        'get name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delete_timer_name)]
    }, fallbacks=[stop_comm]))

    application.add_handler(CommandHandler('lists', lists))

    application.add_handler(CommandHandler('get_id', get_id))

    application.add_handler(ConversationHandler(entry_points=[CommandHandler('create_list', create_list)], states={
        'get name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_list_name)]
    }, fallbacks=[stop_comm]))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('add_member', add_member)], states={
        'member id': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_member_id)]
    }, fallbacks=[stop_comm]))

    application.add_handler(ConversationHandler(entry_points=[CommandHandler('add_points', add_points)], states={
        'points': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_points)]
    }, fallbacks=[stop_comm]))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('del_points', del_points)], states={
        'points': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_del_points)]
    }, fallbacks=[stop_comm]))
    application.add_handler(CommandHandler('check', check_list))
    application.add_handler(CommandHandler('members', list_members))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('exit', exit_list)], states={
        'answer': [MessageHandler(filters.TEXT & ~filters.COMMAND, exit_list_answ)]
    }, fallbacks=[stop_comm]))

    application.add_handler(CommandHandler('gpt', gpt))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('dialog', dialog)], states={
        'process': [MessageHandler(filters.TEXT & ~filters.COMMAND, processing)]
    }, fallbacks=[stop_comm]))
    application.add_handler(ConversationHandler(entry_points=[CommandHandler('image', image)], states={
        'generation': [MessageHandler(filters.TEXT & ~filters.COMMAND, generation)]
    }, fallbacks=[stop_comm]))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    application.run_polling()


if __name__ == '__main__':
    main()
