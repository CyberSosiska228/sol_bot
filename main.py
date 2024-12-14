import telebot
import psycopg2
import json
import solve

settings  = {}
with open("settings.json") as f:
    settings = json.load(f)

pg_connection = psycopg2.connect(database=settings["postgres_settings"]["database"],
                                 host=settings["postgres_settings"]["host"],
                                 user=settings["postgres_settings"]["user"],
                                 password=settings["postgres_settings"]["password"],
                                 port=settings["postgres_settings"]["port"])
print(pg_connection)


bot = telebot.TeleBot(settings["token"])


def pref_check(message, st):
    if (message.text[:len(st)] == st):
        return True
    return False


def ping(message):
    bot.send_message(message.from_user.id, "I am alive!")


def login(message):
    lst = message.text.split("\n")
    try:
        username = lst[1]
        password = lst[2]
    except:
        bot.send_message(message.from_user.id, "Error, check the format of input")
        return

    try:
        cursor = pg_connection.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
        res = cursor.fetchone()

        if (res == None):
            cursor.execute(f"INSERT INTO users (user_id, login, password, solves) VALUES ({message.from_user.id}, \'{username}\', \'{password}\', 0)")
            pg_connection.commit()
            print(f"Added user {message.from_user.id}")
        else:
            cursor.execute(f"UPDATE users SET login = \'{username}\', password = \'{password}\' WHERE user_id = {message.from_user.id}")
            pg_connection.commit()
            print(f"Updated user {message.from_user.id}")
        bot.send_message(message.from_user.id, f"Username: {username}\nPassword: {password}\nSet!")
    except:
        bot.send_message(message.from_user.id, f"Error, make sure, that input is correct. If necessary, please contact admins")


def solve_test(message):
    cursor = pg_connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
    user = cursor.fetchone()
    if (user[3] <= 0):
        bot.send_message(message.from_user.id, f"Not enough credits to solve test, please contact admins")
        return

    try:
        bot.send_message(message.from_user.id, f"Solving...")
        lst = message.text.split()
        res = solve.solve(user[1], user[2], lst[1])
        if (res[0]):
            bot.send_message(message.from_user.id, f"Error wile solving test: \n{res[1]}\n\n(credits will not be spent)\nIf necessary, contact admins")
            return

        cursor.execute(f"UPDATE users SET solves = {user[3] - 1} WHERE user_id = {message.from_user.id}")
        pg_connection.commit()
        bot.send_message(message.from_user.id, f"Done, no errors arise")
    except:
        bot.send_message(message.from_user.id, f"Error, make sure, that input is correct. If necessary, please contact admins")


def check_admin(message):
    if (message.from_user.id not in settings["admins"]):
        return False
    return True

def add(message):
    if (not check_admin(message)):
        bot.send_message(message.from_user.id, f"Permission denied")
        return

    try:
        lst = message.text.split()
        cursor = pg_connection.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_id = {lst[1]}")
        user = cursor.fetchone()

        cursor.execute(f"UPDATE users SET solves = {user[3] + int(lst[2])} WHERE user_id = {message.from_user.id}")
        pg_connection.commit()
        bot.send_message(message.from_user.id, f"Done, no errors arise")
    except:
        bot.send_message(message.from_user.id, f"Error, please check input")


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    if (pref_check(message, "/ping")):
        ping(message)
    if (pref_check(message, "/login")):
        login(message)
    if (pref_check(message, "/solve")):
        solve_test(message)
    if (pref_check(message, "/add")):
        add(message)


while True:
    bot.polling(none_stop=True, interval=0)
