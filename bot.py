#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import logging
import requests

# TO DO: сторонние модули импортируем раньше собственных
from pony.orm import db_session
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import handlers
import intent_settings
from models import UserState, Registration

try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set token!')

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log', encoding='UTF-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)


class Bot:
    """
    Сценарий заказа билетов на самолет и присылка картинки с билетом через vk.vom
    use Python 3.8

    Поддерживает ответ на вопросы: что ты можешь, сценарий заказа билета:
        -спрашивает ФИО
        -спрашивает когда летим
        -спрашивает откуда летим
        -спрашивает куда летим
        -спрашивает какой выбрать рейс из предложенных
        -спрашивает какое кличество мест выбрать
        -спрашивает какой оставить комментарий к заказу
    Если шаг не пройден задаём уточняющий вопрос пока шаг не будет пройден.
    """

    def __init__(self, token, group_id):
        """
        @param token: секретный токен
        @param group_id: group id из группы vk
        """
        self.token = token
        self.group_id = group_id

        self.vk = vk_api.VkApi(token=token, api_version='5.124')
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()
        # self.user_states = {}  # user_id -> UserState

    def run(self):
        """Запуск бота """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as exc:
                log.exception(f'Ошибка в обработке события: {exc}')

    @db_session
    def on_event(self, event):
        """
        Отправляет сообщение обратно, если это текст
        @param event: VKBotMessageEvent object
        @return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info(f'пока не умеем обрабатывать события такого типа - {event.type}')
            return
        user_id = event.message.peer_id
        text = event.message.text

        state = UserState.get(user_id=str(user_id))

        if state is not None:
            self.continue_scenario(text, state, user_id)
        else:
            # ищем интент
            for intent in intent_settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(user_id, intent['scenario'], text)
                    break
            else:
                self.send_text(intent_settings.DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id)

    def send_img(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_date = requests.post(upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_date = self.api.photos.saveMessagesPhoto(**upload_date)

        owner_id = image_date[0]['owner_id']
        media_id = image_date[0]['id']
        access_key = image_date[0]['access_key']
        attachment = f'photo{owner_id}_{media_id}_{access_key}'
        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id)

    def send_step(self, step, user_id, text, context, text_to_send):
        if 'text' in step:
            self.send_text(text_to_send, user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_img(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = intent_settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={}, text_to_send=step['text'])
        UserState(user_id=str(user_id), scenario_name=scenario_name,
                  step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = intent_settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])

        if handler(text=text, context=state.context):
            # следующий шаг
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                if next_step['next_step'] == 'step6':
                    flight_date = str(state.context['date'])
                    takeoff = state.context['takeoff']
                    flights = [flight for flight in handlers.flight_dictionary[flight_date][takeoff]
                               if flight[0] == state.context['arrival']]

                    for i, (city, number_flight, time_flight) in enumerate(flights, 1):
                        text_to_send += f'{i}) Город прилёта - {city} ' \
                                        f'номер рейса - {number_flight} ' \
                                        f'время вылета - {time_flight} \n'
                if next_step['next_step'] == 'step9':
                    text_to_send += f'ФИО - {state.context["fio"]}\n' \
                                    f'Дата вылета - {state.context["date"]}\n' \
                                    f'Город отправления - {state.context["takeoff"]}\n' \
                                    f'Место прилёта - {state.context["arrival"]}\n' \
                                    f'Рейс - {state.context["flight"][1]} {state.context["flight"][2]}\n' \
                                    f'Количество мест - {state.context["place"]}\n' \
                                    f'Комментарий к заказу - {state.context["comment"]}\n'

                self.send_step(next_step, user_id, text, state.context, text_to_send)
                state.step_name = step['next_step']
            else:
                # сценарий закончен
                log.info(state.context)
                Registration(context=state.context)
                text_to_send += state.context['phone_number']
                self.send_step(next_step, user_id, text, state.context, text_to_send)
                state.delete()
        else:
            # остается на текущем
            if state.step_name == 'step2':
                date_list = list(handlers.flight_dictionary.keys())
                text_to_send = f'Допустимые даты для выбора билетов: ' \
                               f'Начиная с - {date_list[0]} ' \
                               f'До - {date_list[-1]}'
            elif state.step_name == 'step3':
                text_to_send = f'Возможные города отлёта: \n'
                for flight_takeoff in handlers.flight_dictionary[state.context['date']]:
                    text_to_send += f'{flight_takeoff}\n'
            elif state.step_name == 'step4':
                if state.context['takeoff'] == text:
                    text_to_send = 'нельзя прилететь в тот же город, откуда выелетели. Доступные города: '
                else:
                    text_to_send = 'нет такого города. Доступные города: '

                flight_date = str(state.context['date'])
                takeoff = state.context['takeoff']
                text_to_send += ', '.join(str(text) for text, *_ in handlers.flight_dictionary[flight_date][takeoff])
            else:
                text_to_send = step['failure_text'].format(**state.context)
            self.send_step(step, user_id, text, state.context, text_to_send)


if __name__ == '__main__':
    bot = Bot(token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.run()
