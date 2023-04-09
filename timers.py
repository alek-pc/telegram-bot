from data.db_session import create_session
from data.timers import Timer
from constants import HELP, MARKUPS
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from main import logger


async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'{context.job.data}')  # после окончания задачи


async def timers(update, context):
    context.user_data['mode'] = 'timer'  # режим - таймер, для определения именнованного таймера
    db_sess = create_session()
    # получаем все пользовательские таймеры для этого пользователя
    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    # выводим их на клавиатуру
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text('Таймеры можно выбрать уже готовый таймер или поставить собственный /set_timer',
                                    reply_markup=markup)


async def stop(update, context):
    await update.message.reply_text('Вышли')
    return ConversationHandler.END


async def edit_timer(update, context):
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
    if any([i not in '1234567890 ' for i in update.message.text]) or len(update.message.text.split()) > 4:
        await update.message.reply_text('Некорректное время, введите время ещё раз')
        return 'get time'
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.name == context.user_data['edit timer conv'],
                                        Timer.user_id == update.effective_user.id).first()

    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(update.message.text.split()[::-1]):
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


async def add_timer(update, context):
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
    if any([i not in '1234567890 ' for i in update.message.text]) or len(update.message.text.split()) > 4:
        await update.message.reply_text('Некорректное время, введите время ещё раз')
        return 'get time'
    db_sess = create_session()
    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(update.message.text.split()[::-1]):
        time[ind] = int(el)
    timer = Timer(name=context.user_data['add timer conv'], seconds=time[0], minutes=time[1], hours=time[2],
                  days=time[3], user_id=update.effective_user.id)
    db_sess.add(timer)
    db_sess.commit()
    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Создан новый таймер {timer.name}', reply_markup=markup)
    return ConversationHandler.END


async def delete_timer(update, context):
    db_sess = create_session()
    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Выберите таймер на клавиатуре, который хотите удалить', reply_markup=markup)
    return 'get name'


async def get_delete_timer_name(update, context):
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id,
                                        Timer.name == update.message.text).first()
    if not timer:
        await update.message.reply_text(f'Таймера {update.message.text} не существует. Выберите таймер на клавиатуре '
                                        f'или выйдите /stop')
        return 'get name'
    db_sess.delete(timer)
    db_sess.commit()

    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Таймер {update.message.text} удален', reply_markup=markup)
    return ConversationHandler.END


async def set_timer(update, context):
    if not context.args or len(context.args) > 4:
        await update.message.reply_text(f"С аргументами что-то не так! Вот инструкция: {HELP['set_timer']}")
        return
    # разбираем аргументы на время - сек, мин, ч, дни
    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(context.args[::-1]):
        time[ind] = int(el)

    chat_id = update.effective_message.chat_id

    data = ''  # для сообщения
    timer_text = ''  # для сообщения о постановку таймера

    if len(context.args) == 4:
        days = 'дней'
        if time[3] % 10 == 1 and time[3] != 11:
            days = 'день'
        elif 2 <= time[3] % 10 <= 4 and not 12 <= time[3] <= 14:
            days = 'дня'
        data += f'{time[3]} {days} '
        timer_text += f'{time[3]} {days} '

    if len(context.args) >= 3:
        hours = 'часов'
        if time[2] % 10 == 1 and time[2] != 11:
            hours = 'час'
        elif 2 <= time[2] % 10 <= 4 and not 12 <= time[2] <= 14:
            hours = 'часа'
        data += f'{time[2]} {hours} '
        timer_text += f'{time[2]} {hours} '

    if len(context.args) >= 2:
        minute = 'минут'
        minute2 = 'минут'
        if time[1] % 10 == 1 and time[1] != 11:
            minute = 'минута'
            minute2 = 'минуту'
        elif 2 <= time[1] % 10 <= 4 and not 12 <= time[1] <= 14:
            minute = 'минуты'
            minute2 = 'минуты'
        data += f'{time[1]} {minute} '
        timer_text += f'{time[1]} {minute2} '

    word = 'истекли'
    sec = 'секунд'
    sec2 = 'секунд'
    if time[0] % 10 == 1 and time[0] != 11:
        sec = 'секунда'
        sec2 = 'секунду'
        word = 'истекла'
    elif 2 <= time[0] % 10 <= 4 and not 12 <= time[0] <= 14:
        sec = 'секунды'
        sec2 = 'секунды'
    data += f'{time[0]} {sec}'
    timer_text += f'{time[0]} {sec2}'

    context.job_queue.run_once(task, time[0] + time[1] * 60 + time[2] * 3600 + time[3] * 3600 * 24, chat_id=chat_id,
                               name=str(chat_id), data=f'{data} {word}')
    await update.message.reply_text(f'Таймер на {timer_text} поставлен')
