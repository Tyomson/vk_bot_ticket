"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True - если шаг пройден и False - если данные введены неверно
"""
import re
import datetime as dt
import json
import random as ra

import pandas as pandas

import intent_settings
from generate_ticket import generate_ticket

pattern_email = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')

pattern_fio = re.compile(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b')
pattern_phone_number = re.compile(r'\b\+?([7,8]\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b')


def handle_dispatcher():
    flight_dictionary = {}
    start_date = dt.date.today()
    end_date = dt.date.today() + dt.timedelta(days=+60)
    range_date = pandas.date_range(start_date, end_date).strftime('%Y-%m-%d').tolist()
    for date in range_date:
        flight_dictionary[date] = {
            departure_city:
                [[arrival_city, ra.randint(100, 10000),
                  str(dt.time(hour=ra.randint(0, 23), minute=+ ra.randint(0, 59)))]
                 for arrival_city in ra.choices(intent_settings.TUPLE_CITIES, k=4)
                 if arrival_city != departure_city]
            for departure_city in intent_settings.TUPLE_CITIES}
    # pprint(flight_dictionary)

    with open('ticket_dictionary.json', 'w', encoding='UTF-8') as file:
        json.dump(flight_dictionary, file)
    return flight_dictionary


flight_dictionary = handle_dispatcher()


def handle_fio(text, context):
    match = pattern_fio.findall(text)
    if match:
        context['fio'] = match[0]
        return True
    else:
        return False


def handle_email(text, context):
    matches = pattern_email.findall(text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def handle_takeoff(text, context):
    try:
        if flight_dictionary[context['date']][text]:
            context['takeoff'] = text
            return True
        else:
            return False
    except KeyError as exc:
        print(exc)
        return False


def handle_arrival(text, context):
    cities = []
    for city in flight_dictionary[context['date']][context['takeoff']]:
        cities.append(city[0])
    if text in cities:
        context['arrival'] = text
        return True
    else:
        return False


def handle_date(text, context):
    try:
        if flight_dictionary[text]:
            context['date'] = str(text)
            return True
        else:
            return False
    except KeyError as exc:
        print(exc)
        return False


def handle_flight(text, context):
    try:
        flight = []
        for voyage in flight_dictionary[context['date']][context['takeoff']]:
            if context['arrival'] in voyage:
                flight.append(voyage)
        if 0 < int(text) <= len(flight):
            context['flight'] = flight[int(text) - 1]
            return True
        else:
            return False
    except (ValueError, IndexError) as exc:
        print(exc)
        return False


def handle_place(text, context):
    try:
        if 0 < int(text) < 6:
            context['place'] = text
            return True
        else:
            return False
    except ValueError as exc:
        print(exc)
        return False


def handle_comment(text, context):
    if len(text) < 1000:
        context['comment'] = text
        return True
    else:
        return False


def handle_confirmation(text, context):
    if text == 'да' or text == 'нет':
        context['confirmation'] = text
        return True
    else:
        return False


def handle_phone_number(text, context):
    matches = pattern_phone_number.findall(text)
    if len(matches) > 0:
        context['phone_number'] = matches[0]
        return True
    else:
        return False


def handle_generate_ticket(text, context):
    return generate_ticket(fio=context['fio'], from_=context['takeoff'], to=context['arrival'],
                           date=context['date'])
