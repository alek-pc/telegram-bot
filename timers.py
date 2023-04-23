from data.db_session import create_session
from data.timers import Timer
from constants import HELP, MARKUPS
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import datetime
from data.users import User


# задача таймера
async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'{context.job.data}')  # после окончания задачи


# раздел таймеров
async def timers(update, context):
    context.user_data['mode'] = 'timers'  # режим - таймер, для определения именнованного таймера
    db_sess = create_session()
    user = db_sess.query(User).filter(User.user_id == int(update.effective_user.id)).first()
    user.last_visit = datetime.datetime.now()
    db_sess.commit()
    # получаем все пользовательские таймеры для этого пользователя
    timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timers'], *user_timers], one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text('Таймеры можно выбрать уже готовый таймер или поставить собственный /set_timer',
                                    reply_markup=markup)


# редактирование таймера - 1ч
async def edit_timer(update, context):
    db_sess = create_session()
    timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
    markup = ReplyKeyboardMarkup([*user_timers, ['/stop']], resize_keyboard=True)
    await update.message.reply_text('Какой таймер будем редактировать? Введите имя', reply_markup=markup)
    return 'get name'


# редактирование таймера 2ч, получение имени таймера
async def get_edit_timer_name(update, context):
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.name == update.message.text,
                                        Timer.user_id == update.effective_user.id).first()
    if not timer:
        await update.message.reply_text('Такого таймера не существует. Введите имя таймера или выйдите /stop')
        return 'get name'
    context.user_data['edit timer conv'] = update.message.text
    await update.message.reply_text('Введите новое имя таймера (если нет, то "нет")',
                                    reply_markup=ReplyKeyboardMarkup([['нет'], ['/stop']], resize_keyboard=True))
    return 'new name'


# редактирование 3ч, новое имя таймера
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
        db_sess.commit()
        context.user_data['edit timer conv'] = timer.name

    await update.message.reply_text('Теперь введите новое время для таймера')
    return 'get time'


# редактирование 4ч, новое время таймера
async def get_edit_timer_time(update, context):
    db_sess = create_session()
    timer = db_sess.query(Timer).filter(Timer.name == context.user_data['edit timer conv'],
                                        Timer.user_id == update.effective_user.id).first()
    if update.message.text.lower() != 'нет':
        if any([i not in '1234567890 ' for i in update.message.text]) or len(update.message.text.split()) > 4:
            await update.message.reply_text('Некорректное время, введите время ещё раз')
            return 'get time'

        time = {0: 0, 1: 0, 2: 0}  # время: 0 - сек, 1 - мин, 2 - ч
        for ind, el in enumerate(update.message.text.split()[::-1]):
            time[ind] = int(el)
        print(time)
        timer.seconds = time[0]
        timer.minutes = time[1]
        timer.hours = time[2]
        db_sess.commit()

    timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timers'], *user_timers], one_time_keyboard=False, resize_keyboard=True)

    await update.message.reply_text(f'Окей. Теперь таймер {timer.name} установлен на {timer.hours} ч '
                                    f'{timer.minutes} мин {timer.seconds} сек', reply_markup=markup)
    return ConversationHandler.END


# новый таймер 1ч
async def add_timer(update, context):
    await update.message.reply_text('Создаем новый таймер. Введите имя нового таймера',
                                    reply_markup=ReplyKeyboardMarkup([['/stop']], resize_keyboard=True))
    return 'get name'


# новый таймер 2ч, имя таймера
async def get_add_timer_name(update, context):
    db_sess = create_session()
    if db_sess.query(Timer).filter(Timer.name == update.message.text,
                                   Timer.user_id == update.effective_user.id).first():
        await update.message.reply_text(f'Таймер {update.message.text} уже существует, выберите другое имя')
        return 'get name'
    context.user_data['add timer conv'] = update.message.text
    await update.message.reply_text(f'Введите время таймера {update.message.text}')
    return 'get time'


# новый таймер 3ч, время таймера
async def get_add_timer_time(update, context):
    if any([i not in '1234567890 ' for i in update.message.text]) or len(update.message.text.split()) > 4:
        await update.message.reply_text('Некорректное время, введите время ещё раз')
        return 'get time'
    db_sess = create_session()
    time = {0: 0, 1: 0, 2: 0}  # время: 0 - сек, 1 - мин, 2 - ч
    for ind, el in enumerate(update.message.text.split()[::-1]):
        time[ind] = int(el)

    timer = Timer(name=context.user_data['add timer conv'], seconds=time[0], minutes=time[1], hours=time[2],
                  user_id=update.effective_user.id)
    db_sess.add(timer)
    db_sess.commit()

    timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timers'], *user_timers], one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(f'Создан новый таймер {timer.name} на {timer.hours} ч '
                                    f'{timer.minutes} мин {timer.seconds} сек', reply_markup=markup)
    return ConversationHandler.END


# удаление таймера 1ч
async def delete_timer(update, context):
    db_sess = create_session()

    timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
    markup = ReplyKeyboardMarkup([*user_timers, ['/stop']], one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(f'Выберите таймер на клавиатуре, который хотите удалить', reply_markup=markup)
    return 'get name'


# удаление таймера 2ч, имя таймера
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

    timers = [el.name for el in db_sess.query(Timer).filter(Timer.user_id == update.effective_user.id)]
    user_timers = [timers[timer: timer + 4] for timer in range(0, len(timers), 4)]
    markup = ReplyKeyboardMarkup([*MARKUPS['timers'], *user_timers], one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(f'Таймер {update.message.text} удален', reply_markup=markup)
    return ConversationHandler.END


# установка собственного таймера
async def set_timer(update, context):
    if not context.args or len(context.args) > 4:
        await update.message.reply_text(f"С аргументами что-то не так! Вот инструкция: {HELP['set_timer']}")
        return
    # разбираем аргументы на время - сек, мин, ч, дни
    time = {0: 0, 1: 0, 2: 0}  # время: 0 - сек, 1 - мин, 2 - ч
    for ind, el in enumerate(context.args[::-1]):
        time[ind] = int(el)

    chat_id = update.effective_message.chat_id

    data = ''  # для сообщения
    timer_text = ''  # для сообщения о постановку таймера

    if len(context.args) == 3:
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

    context.job_queue.run_once(task, time[0] + time[1] * 60 + time[2] * 3600, chat_id=chat_id,
                               name=str(chat_id), data=f'{data} {word}')
    await update.message.reply_text(f'Таймер на {timer_text} поставлен')
