import json


detected_words = 'src/banwords.json'


def load_banwords(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("jew_banwords", [])
    except FileNotFoundError:
        print("Файл не знайдено!")
        return []
    except json.JSONDecodeError:
        print("Помилка у форматі JSON!")
        return []


banwords = load_banwords("banwords.json")


def is_jid(ctx, roles):
    if 'Жидобор' not in roles:
        detected_words = [word for word in banwords if word in ctx.lower()]
        if detected_words:
            return True


def get_ban_words():
    if banwords:
        all_banwords = ", ".join(banwords)  # З'єднання банвордів у рядок
        return all_banwords


def check(msg, roles):
    if is_jid(msg, roles):
        return 'Jid_detected'
    # elif pig_language(msg):
    #     return chose_phrase()
    return False
