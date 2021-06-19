
INTENTS = [
    {
        'name': 'Я могу',
        'tokens': ['/help', 'помощь'],
        'scenario': None,
        'answer': 'Привет. Я помогу Вам выбрать билет и отправлю его. Если хочешь начать напиши - /ticket'
    },
    {
        'name': 'Регистрация',
        'tokens': ['/ticket', 'регистрация'],
        'scenario': 'registration',
        'answer': None
    }
]

SCENARIOS = {
    'registration': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Чтобы создать билет, введите ваше ФИО. Оно будет написано на билете.',
                'failure_text': 'ФИО должно состоять из Фамили* Имени* и Отчества*(при его наличии).'
                                '\n*C большой буквы.',
                'handler': 'handle_fio',
                'next_step': 'step2'
            },
            'step2': {
                'text': 'Напишите дату вылета, например - 2021-05-06',
                'failure_text': 'Дата не распознана.',
                'handler': 'handle_date',
                'next_step': 'step3'
            },
            'step3': {
                'text': 'Напишите город отправления.',
                'failure_text': 'Данный город не найден.',
                'handler': 'handle_takeoff',
                'next_step': 'step4'
            },
            'step4': {
                'text': 'Напишите место прилёта.',
                'failure_text': 'Данный город не найден.',
                'handler': 'handle_arrival',
                'next_step': 'step5'
            },
            'step5': {
                'text': 'Выберите предложенный рейс: \n',
                'failure_text': 'Неверно выбран рейс.',
                'handler': 'handle_flight',
                'next_step': 'step6'
            },
            'step6': {
                'text': 'Выберите количество мест от 1 до 5.',
                'failure_text': 'Неверно выбраны места.',
                'handler': 'handle_place',
                'next_step': 'step7'
            },
            'step7': {
                'text': 'Напишите комментарий к заказу.',
                'failure_text': 'Слишком большой комментарий, максимально возможно 999 символов',
                'handler': 'handle_comment',
                'next_step': 'step8'
            },
            'step8': {
                'text': 'Проверьте правильность введенных данных'
                        ', если все верно напишите "да", в противном случае "нет":\n',
                'failure_text': 'Напишите либо "да", либо "нет" если хотите начать сначала',
                'handler': 'handle_confirmation',
                'next_step': 'step9'
            },
            'step9': {
                'text': 'Введите номер телефона',
                'failure_text': 'Неверно введен номер телефона ожидается - +7 911 912 92 92',
                'handler': 'handle_phone_number',
                'next_step': 'step10'
            },
            'step10': {
                'text': 'С вами свяжутся по номеру - ',
                'image': 'handle_generate_ticket',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }

        }
    }
}

DEFAULT_ANSWER = 'Привет. Я помогу Вам выбрать билет и отправлю его. Если хочешь начать напиши - /ticket'

# TUPLE_CITIES = ['Лондон', 'Париж', 'Уфа', 'Санкт-Петербург', 'Берлин', 'Москва', 'Сочи', 'Стамбул', 'Пекин', 'Токио',
#                 'Нью-Йорк', 'Дрездон', 'Рим', 'Бангкок', 'Лондон', 'Дубай', 'Сингапур', 'Бали', 'Барселона', 'Милан',
#                 'Пхукет', 'Анталья', 'Сеул', 'Каир', 'Афины', 'Флоренция', 'Дублин', 'Ченнаи', 'Орландо', 'Мадрид',
#                 'Джайпур', 'Хошимин', 'Канкун', 'Вена', 'Осака', 'Лас-Вегас', 'Лос-Анджелес', 'Шанхай']

TUPLE_CITIES = ('Лондон', 'Париж', 'Уфа', 'Санкт-Петербург', 'Берлин', 'Москва', 'Вена')


