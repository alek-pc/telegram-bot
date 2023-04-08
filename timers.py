from data.db_session import create_session
from data.timers import Timer
from constants import HELP, MARKUPS
from telegram import ReplyKeyboardMarkup
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


async def add_timer(update, context):
    db_sess = create_session()
    if len(context.args) < 2:
        await update.message.reply_text(f'Введены не все аргументы. {HELP["add_timer"]}')
        return
    if db_sess.query(Timer).filter(Timer.name == context.args[0], Timer.user_id == update.effective_user.id).first():
        await update.message.reply_text(f'Таймер {context.args[0]} уже существует, выберите другое имя')
        return

    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(context.args[1:][::-1]):
        time[ind] = int(el)
    timer = Timer(name=context.args[0], user_id=update.effective_user.id, seconds=time[0], minutes=time[1],
                  hours=time[2], days=time[3])
    db_sess.add(timer)
    db_sess.commit()

    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Создан новый таймер "{context.args[0]}"', reply_markup=markup)


# редактирование таймера /edit_timer <имя таймера> <новое имя (необязательно)> <новое время таймера>
async def edit_timer(update, context):
    db_sess = create_session()

    if len(context.args) < 2:
        await update.message.reply_text(f'Аргументов не хватает! Читайте {HELP["edit_timer"]}')
        return
    timer = db_sess.query(Timer).filter(Timer.name == context.args[0],
                                        Timer.user_id == update.effective_user.id).first()  # редактируемый таймер
    if not timer:
        await update.message.reply_text(f'Таймера "{context.args[0]}" не существует')
        return
    name = timer.name
    if not all([i in '1234567890' for i in context.args[1]]):  # если передано новое имя 2 аргументом
        logger.info(f'new name for timer {timer.name} to {context.args[1]}')
        name = context.args[1]
        if name in [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]:
            await update.message.reply_text(f'Таймер с именем "{name}" уже существует')
            return
    time = {0: 0, 1: 0, 2: 0, 3: 0}  # время: 0 - сек, 1 - мин, 2 - ч, 3 - дни
    for ind, el in enumerate(context.args[1 + int(context.args[1] == name):][::-1]):
        time[ind] = int(el)
    timer.seconds = time[0]
    timer.minutes = time[1]
    timer.hours = time[2]
    timer.days = time[3]
    timer.name = name
    db_sess.commit()

    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Таймер {name} изменен, теперь он на {time[3]} дней {time[2]}ч {time[1]}мин '
                                    f'{time[0]}с', reply_markup=markup)


async def delete_timer(update, context):
    db_sess = create_session()

    if not context.args:
        await update.message.reply_text(f'Какой таймер удалять?! Укажите имя таймера! Читайте {HELP["delete_timer"]}')
        return
    timer = db_sess.query(Timer).filter(Timer.name == context.args[0],
                                        Timer.user_id == update.effective_user.id).first()
    if not timer:
        await update.message.reply_text(f'Таймера {context.args[0]} не существует')
        return

    db_sess.delete(timer)
    db_sess.commit()

    user_timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timer'], user_timers], one_time_keyboard=False)
    await update.message.reply_text(f'Таймер {context.args[0]} удален', reply_markup=markup)


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
