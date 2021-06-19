from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock
import datetime

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot
from handlers import flight_dictionary
from generate_ticket import generate_ticket as gt
import intent_settings as ints

takeoff = list(flight_dictionary[datetime.date.today().strftime('%Y-%m-%d')].keys())[0]
arrival = flight_dictionary[datetime.date.today().strftime('%Y-%m-%d')][takeoff][0][0]


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper


class Test1(TestCase):
    RAW_EVENT = {'type': 'message_new',
                 'object': {'message': {'date': 1616327593, 'from_id': 61194907, 'id': 35, 'out': 0,
                                        'peer_id': 61194907, 'text': 'тест 14', 'conversation_message_id': 18,
                                        'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [],
                                        'is_hidden': False},
                            'client_info': {
                                'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback',
                                                   'intent_subscribe', 'intent_unsubscribe'],
                                'keyboard': True, 'inline_keyboard': True, 'carousel': False, 'lang_id': 0}},
                 'group_id': 202774397, 'event_id': '5f6e389ab73554b00b7bfe8c44c6f201126ac2ec'}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count  # [obj, obj, ...]
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_img = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    INPUTS = [
        'Привет',
        '/help',
        '/ticket',
        'Иван Иванов',
        datetime.date.today().strftime('%Y-%m-%d'),
        takeoff,
        arrival,
        '1',
        '1',
        'supper',
        'да',
        '89151555555',
    ]

    EXPECTED_OUTPUTS = [
        # первое поле текст с которым мы сравниваем ответ бота, второе поле отвечает за то, какую проверку проводим,
        # полную или частичную
        (ints.DEFAULT_ANSWER, True),
        (ints.INTENTS[0]['answer'], True),
        (ints.SCENARIOS['registration']['steps']['step1']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step2']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step3']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step4']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step5']['text'], False),
        (ints.SCENARIOS['registration']['steps']['step6']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step7']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step8']['text'], False),
        (ints.SCENARIOS['registration']['steps']['step9']['text'], True),
        (ints.SCENARIOS['registration']['steps']['step10']['text'], False),
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_img = Mock()
            bot.run()
        assert send_mock.call_count == len(self.INPUTS)

        for (_, kwargs), (expected_output, check) in zip(send_mock.call_args_list, self.EXPECTED_OUTPUTS):
            real_output = kwargs['message']
            if check:
                assert expected_output == real_output
            else:
                assert expected_output in real_output

    def test_painting_ticket(self):
        ticket_bytes = gt('Шанин Артем', 'Москва', 'Уфа', '2020-06-20').getvalue()
        with open('files/test_ticket.png', 'rb') as test_file:
            test_file = test_file.read()
            assert test_file == ticket_bytes
