import sqlite3

from exps import exp
from join_room import join_room, create_room, leave_room, delete_room
from const import bot, SQLITE_FILE, inmarkup_start, markup_2
import telebot.types
from functions import set_last_action, is_turn_over, play_card, discard_card, start_game, vote_card


def new_user(msg):
    user_id = msg.chat.id
    start = msg.text

    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    db.execute("SELECT id FROM alco WHERE id=(?)", (user_id,))
    a = db.fetchone()
    # print(a)

    dont_exist = not bool(a)

    if dont_exist:
        db.execute("INSERT INTO alco (id, lang) VALUES (?, ?)", (user_id, 0,))
    bot.send_message(user_id, "Hello!", reply_markup=inmarkup_start(0))

    if len(start) > 6:
        try:
            room_code = int(start[7:])
            join_room(user_id, room_code)
            bot.send_message(user_id, "You joined room " + str(room_code))
        except:
            bot.send_message(user_id, "shit happens")
    conn.commit()


def get_user(db, m_id):
    sql = "SELECT * FROM alco WHERE ID=?"
    db.execute(sql, [m_id])
    a = db.fetchone()
    return list(a) if a else None

# def join_room(id, room_code):
#    pass


#bot.send_message(354502298, "Ку-ку ёпта!!")


@bot.message_handler(commands=["start"])
def board(message):
    new_user(message)

@bot.message_handler(content_types = ["photo"])
def board1(message):
    if message.chat.id == 900840378:
        bot.send_message(900840378, r'".jpg" : "' + message.photo[2].file_id + r'",')


@bot.callback_query_handler(func=lambda c: c.data == 'create room')
def process_callback_1(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    action = create_room(message.from_user.id, message.message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.callback_query_handler(func=lambda c: c.data == 'join room')
def process_callback_2(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    bot.edit_message_text(text="enter code or follow link",
                          chat_id=message.from_user.id,
                          message_id=message.message.id)
    set_last_action(conn, message.from_user.id, "join")
    conn.commit()


@bot.callback_query_handler(func=lambda c: c.data == 'leave room')
def process_callback_3(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, message.from_user.id)
    room = user[3]
    action = leave_room(message.from_user.id, room, message.message.id)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.callback_query_handler(func=lambda c: c.data == 'delete room')
def process_callback_4(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, message.from_user.id)
    room = user[3]
    action = delete_room(message.from_user.id, room, message.message.id)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.callback_query_handler(func=lambda c: c.data == 'start game')
def process_callback_5(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, message.from_user.id)
    room = user[3]
    action = start_game(conn, message.from_user.id, room, message.message.id)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.callback_query_handler(func=lambda call: call.data[:5] == 'play_')
def process_callback_5(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, message.from_user.id)
    room = user[3]
    action = play_card(conn, message.from_user.id, int(message.data[5]), room, message.message.id)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.callback_query_handler(func=lambda call: call.data[:8] == 'discard_')
def process_callback_6(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, message.from_user.id)
    room = user[3]
    action = discard_card(conn, message.from_user.id, room, int(message.data[8]), message.message.id)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.callback_query_handler(func=lambda call: call.data[:5] == 'vote_')
def process_callback_7(message: telebot.types.CallbackQuery):
    bot.answer_callback_query(message.id)
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, message.from_user.id)
    room = user[3]
    action = vote_card(conn, message.from_user.id, room, int(message.data[5:]), message.message.id)
    set_last_action(conn, message.from_user.id, action)
    conn.commit()


@bot.message_handler(content_types=["text"])
def repeat(message):
    user_id = message.chat.id
    text = message.text
    is_numeric = text.isdigit()
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    user = get_user(db, user_id)
    lang = user[1]
    last_action = user[2]
    room = user[3]

    if is_numeric:
        numbers = int(message.text)
        # join
        if last_action == "join":
            action = join_room(user_id, numbers, room)
            set_last_action(conn, user_id, action)
        # play
        #elif last_action == "play card":
        #    action = play_card(conn, user_id, numbers, room)
        #    set_last_action(conn, user_id, action)
        # discard
        #elif last_action == "discard card":
        #    action = discard_card(conn, user_id, room, numbers)
        #    set_last_action(conn, user_id, action)
        # vote
        #elif last_action == "vote":
        #    action = vote_card(conn, user_id, room, numbers)
        #    set_last_action(conn, user_id, action)



    else:
        pass
        #if text == exp["create room"][lang]:
        #    action = create_room(user_id)
        #    set_last_action(conn, user_id, action)

        #elif text == exp["join room"][lang]:
        #    bot.send_message(user_id, "enter code or follow link")
        #    set_last_action(conn, user_id, "join")

        #if text == exp["leave room"][lang]:
        #    action = leave_room(user_id, room)
        #    set_last_action(conn, user_id, action)

        #elif text == exp["delete room"][lang]:
        #    action = delete_room(user_id, room)
        #    set_last_action(conn, user_id, action)

        #if text == exp["start game"][lang]:
        #    action = start_game(conn, user_id, room)
        #    set_last_action(conn, user_id, action)

        #if text == exp["play card"][lang]:
        #    bot.send_message(user_id, "choose card:", reply_markup=markup_2())
        #    set_last_action(conn, user_id, "play card")

        #elif text == exp["discard card"][lang]:
        #    bot.send_message(user_id, "choose card:", reply_markup=markup_2())
        #    set_last_action(conn, user_id, "discard card")

        #elif text == exp["vote"][lang]:
        #    bot.send_message(user_id, "choose card:", reply_markup=markup_2())
        #    set_last_action(conn, user_id, "vote")

    conn.commit()


if __name__ == '__main__':
    bot.polling(none_stop=True)
