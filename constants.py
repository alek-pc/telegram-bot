BOT_TOKEN = '6188066241:AAFhVK8cuX4oc_1YEi_siFZ-euoFXRNuIK0'  # токен бота
HELP = {'base': """Небольшое объяснение:
/ - это означает, что выполняется какая-то команда, после имени команды, через пробел, можно вводить аргументы""",
        'help': '/help <команда> без указания команды - описание всех команд, при указании конкретной или нескольких - '
                'только её/их описание',
        'timers': '/timers - раздел таймеров: можно выбрать уже существующий\nсоздать (/add_timer)\nредактировать '
                  '(/edit_timer)\nудалять свой таймер (/delete_timer)\nпоставить свой таймер (/set_timer)\nработа со '
                  'временем - /help время',
        'время': 'Установка времени при вводе 1 аргумента - это сек при увеличении: сек -> мин -> часы сначала '
                 '{сек}, потом {мин сек}, {ч мин сек}',
        'set_timer': '/set_timer <время> (/help время) - установка таймера',
        'add_timer': '/add_timer <имя> <время> (/help время) добавляет новый пользовательский таймер в клавиатуру',
        'delete_timer': '/delete_timer удаляет пользовательский таймер с указанным именем',
        'edit_timer': '/edit_timer - редактировать таймер с '
                      'указанным именем: изменение имени таймера (необязательно) и изменение времени (/help время)',
        'lists': '/lists - раздел списков можно: создать новый список (/create_list)\n перейти в уже существующий\n'
                 'просмотреть его содержимое (/check)\nдобавить пункты (/add_points)\nудалить их (/del_points)\n'
                 'добавить участника списка (/add_member)\nвыйти из списка (/exit)',
        'get_id': '/get_id - возвращает id пользователя, который надо вставить в add_member для добавления нового '
                  'участника',
        'create_list': '/create_list - создать новый список',
        'list': '/add_member - добавить пользователя\n/members - все пользователи\n/check - просмотреть содержимое\n'
                '/exit покинуть список\n/add_points - добавить пункты\n/del_points - удалить пункты',
        'add_member': '/add_member - добавить нового участника в список, для этого требуется id пользователя, который '
                      'нужно получить от пользователя, которого хотите добавить в список, с помощью /get_id',
        'members': '/members - все пользователи в этом списке',
        'check': '/check - просмотреть содержимое списка',
        'exit': '/exit - покинуть список',
        'add_points': '/add_points - добавить пункты в список',
        'del_points': '/del_points - удалить пункты из списка',
        'gpt': '/gpt - раздел с доступом к ChatGPT, DALL·E и чему-то ещё\n/dialog - начать диалог\n/image - генерация '
               'изображения по описанию',
        'dialog': '/dialog - начать диалог',
        'image': '/image - генерация изображения по описанию'
        }  # помощь
# все клавиатуры
MARKUPS = {'base': [['/help', '/timers'], ['/lists', '/gpt']],
           'timers': [['/help timers', '/set_timer', '/add_timer'], ['/edit_timer', '/delete_timer', '/back']],
           'lists': [['/help lists', '/get_id'], ['/create_list', '/back']],
           'concrete list': [['/help list', '/add_member'], ['/check', '/add_points', '/del_points'],
                             ['/members', '/exit', '/back']],
           'gpt': [['/help gpt', '/back'], ['/dialog', '/image']]
           }
# headers для gpt
GPT_HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "ed2a8864e6mshcc3580b4c59740dp178069jsn87d27bcaca81",
    "X-RapidAPI-Host": "openai80.p.rapidapi.com"
}
URLS = {
    'text': "https://openai80.p.rapidapi.com/chat/completions",
    'images': 'https://openai80.p.rapidapi.com/images/generations'
}
PAYLOADS = {
    'text': {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "Hello!"
            }
        ]
    },
    'images': {
        "prompt": "A cute baby sea otter",
        "n": 1,
        "size": "1024x1024"}
}
