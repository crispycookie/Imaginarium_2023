import json
from random import randint
import sqlite3
import random

from cards import crd
from const import DEBUG, bot, max_users, SQLITE_FILE, inmarkup_roominfo, inmarkup_roomcreator, inmarkup_start


def join_room(id, code, room):
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    if room:
        sql = "SELECT creator_id FROM rooms WHERE room_id = ?"
        db.execute(sql, (room,))
        creator = db.fetchone()[0]
        if id == creator:
            bot.send_message(text="You are already in room!!!", chat_id=id, reply_markup=inmarkup_roomcreator(0))
        else:
            bot.send_message(text="You are already in room!!!", chat_id=id, reply_markup=inmarkup_roominfo(0))
        db.close()
        return "join_error_already_in_room"
        
    sql = "SELECT players_amount FROM rooms WHERE room_id=?"
    db.execute(sql, (code,))
    try:
        amount = db.fetchone()[0]
        if amount < max_users:
            sql = "UPDATE alco SET (room, turn_over, queue) = (?, ?, ?) WHERE ID=?"
            db.execute(sql, (code, 0, amount+1, id,))
            sql = "UPDATE rooms SET players_amount=? WHERE room_id = ?"
            db.execute(sql, (amount+1, code,))

            # !!!!!!!!!!!!!!!!!!!!
            sql = "SELECT deck FROM rooms WHERE room_id=?"
            db.execute(sql, (code,))
            deck = json.loads(db.fetchone()[0])
            hand = []
            for i in range(6):
                hand.append(deck[0])
                deck.pop(0)
            hand = json.dumps(hand).encode('utf-8')
            deck = json.dumps(deck).encode('utf-8')

            sql = "UPDATE alco SET hand = ? WHERE id = ?"
            db.execute(sql, (hand, id,))

            sql = "UPDATE rooms SET deck = ? WHERE room_id = ?"
            db.execute(sql, (deck, code,))

            bot.send_message(text="You joined room, wait for game start.", chat_id=id, reply_markup=inmarkup_roominfo(0))
            db.close()
            conn.commit()
            return "join_success"
        else:
            bot.send_message(text="current room is full", chat_id=id, reply_markup=inmarkup_start(0))
            db.close()
            conn.commit()
            return "join_error_room_is_full"
    except:
        bot.send_message(text="Invalid room id", chat_id=id, reply_markup=inmarkup_start(0))
        db.close()
        return "join_error_invalid_room"


def leave_room(id, code, message_id):
    if not code:
        bot.edit_message_text(text="You are already not in room!!!",
                              chat_id=id, message_id=message_id, reply_markup=inmarkup_start(0))
        return "leave_error_already_not_in_room"

    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    sql = "SELECT creator_id, players_amount FROM rooms WHERE room_id=?"
    db.execute(sql, (code,))
    creator_id, amount = db.fetchone()
    if creator_id == id:
        bot.edit_message_text(text="You are creator and can`t leave this room (only delete)!!!",
                              chat_id=id, message_id=message_id, reply_markup=inmarkup_roomcreator(0))
        db.close()
        conn.commit()
        return "leave_error_creator_leaveator"
    else:

        sql = "UPDATE alco SET room=? WHERE ID=?"
        db.execute(sql, (None, id,))
        sql = "UPDATE rooms SET players_amount=? WHERE room_id = ?"
        db.execute(sql, (amount-1, code,))
        bot.edit_message_text(text="You left this room.",
                              chat_id=id, message_id=message_id, reply_markup=inmarkup_start(0))
        db.close()
        conn.commit()
        return "leave_success"


def create_room(user_id, message_id):
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    sql = "SELECT room FROM alco WHERE id = ?"
    db.execute(sql, (user_id,))
    room = db.fetchone()[0]
    if room:
        sql = "SELECT creator_id FROM rooms WHERE room_id = ?"
        db.execute(sql, (room,))
        creator = db.fetchone()[0]
        if user_id == creator:
            bot.send_message(text="You are already in room!!!", chat_id=user_id, reply_markup=inmarkup_roomcreator(0))
        else:
            bot.send_message(text="You are already in room!!!", chat_id=user_id, reply_markup=inmarkup_roominfo(0))
        db.close()
        return "create_error_already_in_room"
        
    new_room_id = generate_code()

    deck = [i for i in range(len(crd))]
    random.shuffle(deck)
    deck = json.dumps(deck).encode('utf-8')


    sql = "INSERT INTO rooms(room_id, creator_id, deck) VALUES (?, ?, ?)"
    db.execute(sql, (new_room_id, user_id, deck,))

    #!!!!!!!!!!!!!!!!!!!!
    sql = "SELECT deck FROM rooms WHERE room_id=?"
    db.execute(sql, (new_room_id,))
    deck = json.loads(db.fetchone()[0])
    hand = []
    for i in range(6):
        hand.append(deck[0])
        deck.pop(0)
    hand = json.dumps(hand).encode('utf-8')
    deck = json.dumps(deck).encode('utf-8')

    sql = "UPDATE alco SET (room, queue, hand) =(?, ?, ?) WHERE id = ?"
    db.execute(sql, (new_room_id, 1, hand, user_id,))

    sql = "UPDATE rooms SET deck = ? WHERE room_id = ?"
    db.execute(sql, (deck, new_room_id,))
        
    db.close()
    bot.edit_message_text(text="*ROOM INFO*\n\n\nYour room code is:\n" + str(new_room_id),
                          chat_id=user_id, message_id=message_id, reply_markup=inmarkup_roomcreator(0))
    conn.commit()
    return "create_success"


def delete_room(user_id, room, message_id):
    if room:
        conn = sqlite3.connect(SQLITE_FILE)
        db = conn.cursor()
        sql = "SELECT creator_id FROM rooms WHERE room_id=?"
        db.execute(sql, (room,))
        creator_id = db.fetchone()[0]
        if creator_id == user_id:
            sql = "UPDATE alco SET room=? WHERE room=?"
            db.execute(sql, (None, room,))
            sql = "DELETE FROM rooms WHERE room_id = ?"
            db.execute(sql, (room,))
            db.close()
            conn.commit()
            bot.edit_message_text(text="You have successfully deleted this room.",
                                  chat_id=user_id, message_id=message_id, reply_markup=inmarkup_start(0))
            return "delete_success"
        else:
            bot.edit_message_text(text="You are not an admin of this room.",
                                  chat_id=user_id, message_id=message_id, reply_markup=inmarkup_roominfo(0))
            return "delete_fail_not_admin"
    else:
        bot.edit_message_text(text="You are not in room now.",
                              chat_id=user_id, message_id=message_id, reply_markup=inmarkup_start(0))
        return "delete_fail_not_in_room"


def generate_code():
    conn = sqlite3.connect(SQLITE_FILE)
    db = conn.cursor()
    sql = "SELECT room_id FROM rooms"
    db.execute(sql)
    room_ids = db.fetchall()
    if DEBUG: print("join_room.py: room_ids:", room_ids)
    
    found = False
    new_room_id = 0
    while not found:
        new_room_id = randint(100000, 999999)
        if [new_room_id] not in room_ids:
            found = True
    return new_room_id  
    
    
