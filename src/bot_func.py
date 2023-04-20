import gaussian_sollution
CONTENT_WORDS = ["жид", "жиди", "жидо-бандерівець", "жидо-бандеравець", "жидобор", "жидо-бандера", "жидобандерівець",
                 "jid", "жидів", "жидами", "жида", "жидах", "жидом", "жиду", "жидам", "жиді", ";bl", ":bl", ";blb",
                 ":blb"]


def help_fun():
    """"Help function"""
    return 'Here is some help about bot\n' \
           '.check_all_ban_words - get all ban words on this server'


def get_ban_words():
    return CONTENT_WORDS


def gaussian_method(msg):
    msg = msg.split(" ", 1)
    formula = msg[1]

    return gaussian_sollution.final_res(formula)
