import bot_func
import langid
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


def is_jid(msg, roles):
    if 'Жидобор' not in roles:
        for ban_word in bot_func.get_ban_words():
            if ban_word in msg.lower():
                return True


def pig_language(msg):
    if langid.classify(msg)[0] in ['ru', 'bg']:
        return True


def chose_phrase():
    phrase_num = random.randrange(0, 8)
    return PHRASES[phrase_num]


def check(msg, roles):
    if is_jid(msg, roles):
        return 'Jid_detected'
    elif pig_language(msg):
        return chose_phrase()
    return False
