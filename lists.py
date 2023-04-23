from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup
from data.lists import List
from data.users import User
from data.db_session import create_session
from constants import MARKUPS
from random import choice
import datetime


# переход в раздел списков
async def lists(update, context):
    db_sess = create_session()
    context.user_data['mode'] = 'lists'
    personal_lists = [el.name for el in db_sess.query(List).all() if str(update.effective_user.id) in
                      el.members.split(';')]
    personal_lists = [personal_lists[x: x + 3] for x in range(0, len(personal_lists), 3)]

    user = db_sess.query(User).filter(User.user_id == int(update.effective_user.id)).first()
    user.last_visit = datetime.datetime.now()
    db_sess.commit()

    await update.message.reply_text('Вы попали в раздел списков',
                                    reply_markup=ReplyKeyboardMarkup([*MARKUPS['lists'], *personal_lists],
                                                                     one_time_keyboard=False, resize_keyboard=True))


# проверить содержимое списка
async def check_list(update, context):
    db_sess = create_session()
    sh_list = [el.points for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all()
               if str(update.effective_user.id) in el.members.split(';')][0]
    points = '\n'.join(sh_list.split(';'))
    if not points:
        points = 'В списке пока что пусто'
    await update.message.reply_text(points)


# добавить участника в список - ч1
async def add_member(update, context):
    await update.message.reply_text('какого пользователя вы хотите добавить? Введите id',
                                    reply_markup=ReplyKeyboardMarkup([['/stop']], resize_keyboard=True))
    return 'member id'


# добавить участника 2ч, получение id этого пользователя
async def get_member_id(update, context):
    db_sess = create_session()
    user = db_sess.query(User).filter(User.user_id == int(update.message.text)).first()
    if not user:
        await update.message.reply_text('Этот пользователь не пользуется мной. Попробуйте ввести id пользователя снова '
                                        'или /stop')
        return 'member id'
    edit_list = [el for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all() if
                 str(update.effective_user.id) in el.members][0]
    edit_list.members += f'{update.message.text};'
    db_sess.commit()
    await update.message.reply_text(f'Пользователь присоединен к списку')
    return ConversationHandler.END


# просмотреть участников списка
async def list_members(update, context):
    db_sess = create_session()
    members = [el for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all()
               if str(update.effective_user.id) in el.members.split(';')][0].members.split(';')
    names = [db_sess.query(User).filter(User.user_id == int(el)).first().name for el in members]
    await update.message.reply_text(f'Участники списка: {", ".join(names)}')


# получение id пользователя для его добавления в список
async def get_id(update, context):
    await update.message.reply_text(f'Вот ваш id: {update.effective_user.id}')


# добавить пункты в список - 1ч
async def add_points(update, context):
    await update.message.reply_text('Итак, будем добавлять в список пункты! С чего начнем?',
                                    reply_markup=ReplyKeyboardMarkup([['/stop']], resize_keyboard=True))
    return 'points'


# пункты в список 2ч, получение пунктов
async def get_points(update, context):
    db_sess = create_session()
    sh_list = [el for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all()
               if str(update.effective_user.id) in el.members][0]
    sh_list.points += f'{update.message.text};'
    db_sess.commit()
    return 'points'


# удалить пункты списка - 1ч
async def del_points(update, context):
    db_sess = create_session()
    sh_list = [el for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all()
               if str(update.effective_user.id) in el.members][0]
    points = sh_list.points.split(';')
    points = [points[x: x + 3] for x in range(0, len(points), 3)]
    await update.message.reply_text('Удаляем пункты',
                                    reply_markup=ReplyKeyboardMarkup([*points, ['/stop']],
                                                                     one_time_keyboard=False, resize_keyboard=True))
    return 'points'


# удалить пункты - 2ч, получение пунктов
async def get_del_points(update, context):
    db_sess = create_session()
    sh_list = [el for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all()
               if str(update.effective_user.id) in el.members][0]
    points = sh_list.points.split(';')
    sh_list.points = ';'.join(points[:points.index(points[::-1][points[::-1].index(update.message.text)])] + \
                              points[points.index(points[::-1][points[::-1].index(update.message.text)]) + 1:])
    db_sess.commit()
    points = sh_list.points.split(';')
    points = [points[x: x + 3] for x in range(0, len(points) + 3)]
    await update.message.reply_text(choice(['Ну ок', 'Окей', 'Ясно', '...']),
                                    reply_markup=ReplyKeyboardMarkup([*points, ['/stop']],
                                                                     one_time_keyboard=False, resize_keyboard=True))
    return 'points'


# создание списка - 1ч
async def create_list(update, context):
    await update.message.reply_text('Так-с начнем создавать список. Какое будет имя у этого списка?',
                                    reply_markup=ReplyKeyboardMarkup([['/stop']], resize_keyboard=True,
                                                                     one_time_keyboard=False))
    return 'get name'


# создание списка - 2ч, получение имени
async def get_list_name(update, context):
    db_session = create_session()
    if [el for el in db_session.query(List).filter(List.name == update.message.text).all()
        if str(update.effective_user.id) in el.members]:
        await update.message.reply_text('Вы уже состоите в списке с таким же именем. Введите другое имя или /stop')
        return 'get name'
    new_list = List(name=update.message.text, members=str(update.effective_user.id))
    db_session.add(new_list)
    db_session.commit()

    context.user_data['mode'] = 'concrete list'
    context.user_data['list name'] = update.message.text

    await update.message.reply_text(f'Всё, список {new_list.name} создан. Пока что в нем состоите только вы, можно '
                                    f'пригласить людей если они скинут свои id через /get_id и записать id /add_member',
                                    reply_markup=ReplyKeyboardMarkup([*MARKUPS['concrete list']],
                                                                     resize_keyboard=True, one_time_keyboard=False))
    return ConversationHandler.END


# выйти из списка - 1ч
async def exit_list(update, context):
    await update.message.reply_text(f'Вы уверены, что хотите выйти из списка {context.user_data["list name"]}?',
                                    reply_markup=ReplyKeyboardMarkup([['да', 'нет']], resize_keyboard=True))
    return 'answer'


# выйти из списка - 2ч, подтверждение
async def exit_list_answ(update, context):
    db_sess = create_session()
    if update.message.text == 'да':
        sh_list = [el for el in db_sess.query(List).filter(List.name == context.user_data['list name']).all()
                   if str(update.effective_user.id) in el.members.split(';')][0]
        points = sh_list.members.split(';')
        sh_list.members = ";".join(points[:points.index(str(update.effective_user.id))] +
                                   points[points.index(str(update.effective_user.id)) + 1:])
        if not sh_list.members:
            db_sess.delete(sh_list)
        db_sess.commit()
        personal_lists = [el.name for el in db_sess.query(List).all() if str(update.effective_user.id) in el.members]
        personal_lists = [personal_lists[x: x + 3] for x in range(0, len(personal_lists), 3)]

        await update.message.reply_text('Вы вышли из этого списка',
                                        reply_markup=ReplyKeyboardMarkup([*MARKUPS['lists'], *personal_lists],
                                                                         one_time_keyboard=False, resize_keyboard=True))
    else:
        personal_lists = [el.name for el in db_sess.query(List).all() if str(update.effective_user.id) in el.members]
        personal_lists = [personal_lists[x: x + 3] for x in range(0, len(personal_lists), 3)]

        await update.message.reply_text('Ну передумали, так передумали...',
                                        reply_markup=ReplyKeyboardMarkup([*MARKUPS['lists'], *personal_lists],
                                                                         one_time_keyboard=False, resize_keyboard=True))
    context.user_data['mode'] = 'lists'
    return ConversationHandler.END
