BOT_TOKEN = '6188066241:AAFhVK8cuX4oc_1YEi_siFZ-euoFXRNuIK0'
HELP = {'base': """Небольшое объяснение:
/ - это означает, что выполняется какая-то команда, после имени команды, через пробел, можно вводить аргументы""",
        'help': '/help <команда> без указания команды - описание всех команд, при указании конкретной или нескольких - '
                'только её/их описание',
        'timers': '/timers - раздел таймеров можно выбрать уже существующий, создать (/add_timer), редактировать '
                  '(/edit_timer) и удалять свой таймер (/delete_timer), ставить свой таймер (/set_timer)',
        'set_timer': '/set_timer <время>- установка таймера; по умолчанию нужно вводить 1 аргумент - время в секундах, '
                     'при увеличении кол-ва аргументов время переходит вот так: сек -> мин -> часы -> дни сначала {сек}'
                     ', потом {мин сек}, {ч мин сек}',
        'add_timer': '/add_timer <имя> <время (как с timer)> добавляет новый пользовательский таймер в клавиатуру',
        'delete_timer': '/delete_timer удаляет пользовательский таймер с указанным именем',
        'edit_timer': '/edit_timer - редактировать таймер с '
                      'указанным именем: изменение имени таймера (необязательно) и изменение времени (как с timer)'
        }
MARKUPS = {'base': [['/help', '/timers'], ['/lists']],
           'timers': [['/help timers', '/set_timer', '/add_timer'], ['/edit_timer', '/delete_timer', '/back']],
           'lists': [['/add_member', '/add_point', '/add_list', '/back']]
           }
