import bot_func
from langdetect import detect, LangDetectException
from googletrans import Translator
import random

PHRASES = ['Не пукай',
           'Хрюкни ще раз, в тебе непогано виходить',
           'Свинко, ти забула де твій хлів знаходиться?',
           'А тепер напиши те ж саме, тільки нормальною мовою.',
           'Погано розумію свинособачу, а ну-мо повтори ще разок.',
           'Я не знаю російської. Може спробуєш державною?',
           'Не розумію про що ти. Щось на роснявій...',
           'Друзі, наша русофобія недостатня.',
           'Як ти потішно хрюкаєш.', ]

ANTI_RUSSIAN_GIFS = [
    'https://tenor.com/bMadz.gif',
    'https://tenor.com/bU86p.gif',
    'https://tenor.com/bP63X.gif',
    'https://tenor.com/bSSFC.gif',
    'https://tenor.com/bCFHn.gif',
    'https://tenor.com/bGK77.gif',
    'https://tenor.com/bVCko.gif',
    'https://tenor.com/bN5vM.gif',
    'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGIxYjU3NTBlOGU1MTc0OGRlNTRlZjk1ZmU3MzIxYmEwMWU0ZGFlYyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/F9nce11rm09KJ6dWtc/giphy.gif',
    'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWE0MzI5Mjc2MzMyMzVmN2ZkY2QxN2FjYWY2NWY2YWQzYmQxYzhiYyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/FHbY8ZKhEXNBIIIivF/giphy.gif',
    'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMThiZGNlYzA3YzdiNzliMDMyNGNjY2M0MzcyYzIyMDAwMmEyNmQwMCZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/Ebfaj7RRiMwLT5saCj/giphy.gif',
    'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2ZmNmIzMzY1Y2ZlNTFmY2UxZWE4Mzk5NzdlNjFjZDNiOTY2MjlmNSZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/QR7GVCUJYOYYxAy08l/giphy.gif',
    'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2FhMmVhNTMxZTMyNDgxM2I2MWU4ZTNlMzAzMzk1ZDE5ZTA2ZmY4NCZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/m55jtQoAAlI9MX0jMy/giphy.gif',

]


def is_jid(msg, roles):
    if 'Жидобор' not in roles:
        for ban_word in bot_func.get_ban_words():
            if ban_word in msg.lower():
                return True


def pig_language(msg):

    lang = detect(msg)

    if lang == 'ru' and lang != 'uk':
        translator = Translator(service_urls=['translate.google.com'])
        translation = translator.translate(msg, dest='ru')
        return translation.src == 'ru'


def chose_phrase():
    is_gif = random.choice([True, False])

    if is_gif:
        gif_send = random.choice(ANTI_RUSSIAN_GIFS)
        return gif_send
    else:
        phrase = random.choice(PHRASES)
        return phrase


def check(msg, roles):
    if is_jid(msg, roles):
        return 'Jid_detected'
    elif pig_language(msg):
        return chose_phrase()
    return False
