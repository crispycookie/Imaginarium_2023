import sqlite3
import json
import random
from cards import crd

import telebot.types

from const import bot, SQLITE_FILE, markup_1, markup_2, \
    inmarkup_roominfo, inmarkup_roomcreator, inmarkup_play, inmarkup_discard, inmarkup_vote


def set_last_action(conn, user_id, action):
    db = conn.cursor()
#    conn = sqlite3.connect("imagination.db")
    sql = "UPDATE alco SET last_action=? WHERE ID=?"
    db.execute(sql, (action, user_id))
    db.close()

def is_turn_over(conn, user_id):
    db = conn.cursor()
    sql = "SELECT turn_over FROM alco WHERE id=?"
    db.execute(sql, (user_id,))
    is_over = db.fetchone()[0]
    db.close()
    return is_over


def start_game(conn, user_id, room, message_id):
    if room:
        db = conn.cursor()
        sql = "SELECT creator_id, players_amount, is_started FROM rooms WHERE room_id=?"
        db.execute(sql, (room,))
        creator_id, players_amount, is_started = db.fetchall()[0]
        if is_started:
            bot.delete_message(chat_id=user_id, message_id=message_id)
            bot.send_message(user_id, "Your game is already started.")
            return "start_fail_already_started"
        elif creator_id != user_id:
            bot.edit_message_text(text="You are not an admin of this room.",
                                  chat_id=user_id, message_id=message_id, reply_markup=inmarkup_roominfo(0))
            return "start_fail_not_admin"
        elif players_amount < 3-1:
            bot.edit_message_text(text="You can`t start game with less than 3 players.",
                                  chat_id=user_id, message_id=message_id, reply_markup=inmarkup_roomcreator(0))
            return "start_fail_not_enough_players"
        else:
            sql = "SELECT id FROM alco WHERE room=?"
            db.execute(sql, (room,))
            players = db.fetchall()
            sql = "SELECT creator_id FROM rooms WHERE room_id=?"
            db.execute(sql, (room,))
            current_player = db.fetchone()[0]
            sql = "UPDATE rooms SET (is_started, current_player) = (?, ?) WHERE room_id=?"
            db.execute(sql, (1, current_player, room))
            sql = "UPDATE alco SET turn_over = ? WHERE room=?"
            db.execute(sql, (0, room,))
            for player in players:
                player = player[0]
                sql = "SELECT hand FROM alco WHERE id = ?"
                db.execute(sql, (player,))
                hand = json.loads(db.fetchone()[0])
                for i in range(len(hand)):
                    if i == 0:
                        hand[i] = telebot.types.InputMediaPhoto(crd[str(hand[i]) + ".jpg"],
                                                                caption="Your cards")
                    else:
                        hand[i] = telebot.types.InputMediaPhoto(crd[str(hand[i]) + ".jpg"])
                if player != current_player:
                    media_group = bot.send_media_group(player, hand)
                    sql = "UPDATE alco SET mediagroup = ? WHERE id = ?"
                    db.execute(sql, (media_group[0].message_id, player))
                    message = bot.send_message(text="Your game has started. Wait, current player is choosing card",
                                          chat_id=player)
                    sql = "UPDATE alco SET message = ? WHERE id=?"
                    db.execute(sql, (message.message_id, player,))
                else:
                    #CHANGE START MESSAGE FORM

                    #bot.delete_message(chat_id=player, message_id=message_id)
                    media_group = bot.send_media_group(chat_id=player, media=hand)
                    sql = "UPDATE alco SET mediagroup = ? WHERE id = ?"
                    print(media_group[0].message_id)
                    db.execute(sql, (media_group[0].message_id, current_player))
                    bot.send_message(text="Your turn! Choose card.",
                                          chat_id=current_player, reply_markup=inmarkup_play())
            return "start_success"
    else:
        bot.send_message(user_id, "You ARE NOT IN ROM NOW.")
        return "start_fail_not_in_room"


def play_card(conn, user_id, card_hand_number, room, message_id):
    db = conn.cursor()

    sql = "SELECT current_player, is_started FROM rooms WHERE room_id=?"
    db.execute(sql, (room,))
    current_player, game_status = db.fetchall()[0]
    print(game_status)

    if user_id == current_player and (not is_turn_over(conn, user_id)) and room and game_status==1:
        sql = "SELECT hand FROM alco WHERE id=?"
        db.execute(sql, (user_id,))
        hand = json.loads(db.fetchone()[0])
        card_unic_number = hand[card_hand_number-1]

        sql = "UPDATE alco SET (turn_over, discard) = (?, ?) WHERE id=?"
        db.execute(sql, (1, card_unic_number, user_id,))

        sql = "SELECT id FROM alco WHERE room = ?"
        db.execute(sql, (room,))
        players = db.fetchall()
        message = bot.edit_message_text(text="Played, thanks. Discard turn now",
                              chat_id=current_player, message_id=message_id)
        sql = "UPDATE alco SET message = ? WHERE id = ?"
        db.execute(sql, (message.message_id, current_player))

        for player in players:
            player = player[0]
            sql = "SELECT message FROM alco WHERE id = ?"
            db.execute(sql, (player,))
            old_message_id = db.fetchone()[0]
            if player != current_player:
                bot.edit_message_text(text="Discard turn. Please choose one",
                                      chat_id=player, message_id=int(old_message_id),
                                      reply_markup=inmarkup_discard())
        db.close()
        return "card_played"
    else:
        print(user_id, current_player, is_turn_over(conn, user_id), room, game_status)
        bot.send_message(text="You are not allowed to play card now", chat_id=user_id)
        db.close()
        return "error_card_play"

def discard_card(conn, user_id, room, card_hand_number, message_id):
    db = conn.cursor()
    sql = "SELECT current_player, is_started FROM rooms WHERE room_id=?"
    db.execute(sql, (room,))
    current_player, game_status = db.fetchall()[0]
    sql = "SELECT turn_over FROM alco WHERE id=?"
    db.execute(sql, (current_player,))
    current_player_done = db.fetchone()[0]
    print(user_id)

    if (not is_turn_over(conn, user_id)) and current_player_done and room and user_id!=current_player and game_status==1:
        sql = "SELECT hand FROM alco WHERE id=?"
        db.execute(sql, (user_id,))
        hand = json.loads(db.fetchone()[0])
        card_unic_number = hand[card_hand_number-1]

        sql = "UPDATE alco SET turn_over = ? WHERE id=?"
        db.execute(sql, (1, user_id,))
        sql = "UPDATE alco SET discard = ? WHERE id=?"
        db.execute(sql, (card_unic_number, user_id,))

        sql = "SELECT discard FROM alco WHERE turn_over = 1 AND room = ?"
        db.execute(sql, (room,))
        discards = db.fetchall()
        discards.sort()
        for i in range(len(discards)):
            discards[i] = discards[i][0]

        sql = "SELECT players_amount FROM rooms WHERE room_id=?"
        db.execute(sql, (room,))
        players_amount = db.fetchone()[0]

        if len(discards) == players_amount:
            sql = "UPDATE rooms SET is_started=? WHERE room_id=?"
            db.execute(sql, (2, room,))
            sql = "SELECT id FROM alco WHERE room=?"
            db.execute(sql, (room,))
            players = db.fetchall()
            for player in players:
                player = player[0]
                if player != current_player:
                    sql = "UPDATE alco SET turn_over = ? WHERE id = ?"
                    db.execute(sql, (0, player,))
                sql = "SELECT discard FROM alco WHERE room = ?"
                db.execute(sql, (room,))
                discards = db.fetchall()
                discards.sort()
                for i in range(len(discards)):
                    if i == 0:
                        discards[i] = telebot.types.InputMediaPhoto(crd[str(discards[i][0]) + ".jpg"],
                                                                    caption="Discarded cards")
                    else:
                        discards[i] = telebot.types.InputMediaPhoto(crd[str(discards[i][0]) + ".jpg"])

                voted_cards = bot.send_media_group(chat_id=player, media=discards)
                sql = "UPDATE alco SET votedcards = ? WHERE id = ?"
                db.execute(sql, (voted_cards[0].message_id, player))
                if player == current_player:
                    sql = "SELECT message FROM alco WHERE id = ?"
                    db.execute(sql, (player,))
                    old_message_id = db.fetchone()[0]
                    print(old_message_id, "OLD MESSAGE ID", player)
                    message = bot.edit_message_text(text="Wait for voting end",
                                          chat_id=current_player, message_id=int(old_message_id))
                    sql = "UPDATE alco SET message = ? WHERE id = ?"
                    db.execute(sql, (message.message_id, current_player))
                else:
                    sql = "SELECT message FROM alco WHERE id = ?"
                    db.execute(sql, (player,))
                    old_message_id = db.fetchone()[0]
                    message = bot.edit_message_text(text="Choose one card and vote",
                                          chat_id=player, message_id=int(old_message_id),
                                          reply_markup=inmarkup_vote(players_amount))
                    sql = "UPDATE alco SET message = ? WHERE id = ?"
                    db.execute(sql, (message.message_id, player))
        db.close()
        return "card_discarded"
    else:
        bot.send_message(user_id, "you are not allowed to discard card now")
        db.close()
        return "error_card_discard"


def vote_card(conn, user_id, room, vote_hand_number, message_id):
    db = conn.cursor()
    sql = "SELECT current_player, is_started, players_amount FROM rooms WHERE room_id=?"
    db.execute(sql, (room,))
    current_player, game_status, players_amount = db.fetchall()[0]
    sql = "SELECT turn_over, discard, hand FROM alco WHERE id=?"
    db.execute(sql, (user_id,))
    turn_over, discard, hand = db.fetchall()[0]
    print(hand, type(hand))
    if (not is_turn_over(conn, user_id)) and room and user_id != current_player and game_status == 2:
        sql = "SELECT discard FROM alco WHERE room = ?"
        db.execute(sql, (room,))
        discards = db.fetchall()
        discards.sort()
        for i in range(len(discards)):
            discards[i] = discards[i][0]
        vote_unic_number = discards[vote_hand_number-1]
        if vote_unic_number != discard:
            sql = "UPDATE alco SET (vote, turn_over) = (?, ?) WHERE id=?"
            db.execute(sql, (vote_unic_number, 1, user_id,))
            sql = "SELECT id FROM alco WHERE (room = ? AND turn_over = 1)"
            db.execute(sql, (room,))
            users_id = db.fetchall()
            if len(users_id) == players_amount:
                for user in users_id:
                    user = user[0]
                    sql = "SELECT score, discard, vote, hand FROM alco WHERE id = ?"
                    db.execute(sql, (user,))
                    score, discard, vote, hand = db.fetchall()[0]
                    sql = "SELECT vote FROM alco WHERE room = ?"
                    db.execute(sql, (room,))
                    votes = db.fetchall()
                    sql = "SELECT discard FROM alco WHERE id = ?"
                    db.execute(sql, (current_player,))
                    correct = db.fetchone()
                    change = 0
                    if user == current_player:
                        for one in votes:
                            one = one[0]
                            if one == correct:
                                change += 1
                        if change != players_amount and change !=0:
                            change += 3
                    else:
                        for one in votes:
                            one = one[0]
                            if one == discard:
                                change += 1
                        if vote == correct:
                            change += 2
                    score += change
                    sql = "UPDATE alco SET score = ? WHERE id = ?"
                    db.execute(sql, (score, user,))
                    sql = "SELECT queue FROM alco WHERE id = ?"
                    db.execute(sql, (user,))
                    queue = db.fetchone()[0]
                    if queue == 1:
                        queue = players_amount
                    else:
                        queue -= 1
                    if queue == 1:
                        new_current_player = user
                    sql = "UPDATE alco SET (queue, turn_over) = (?, ?)  WHERE id = ?"
                    db.execute(sql, (queue, 0, user,))
                    hand = json.loads(hand)
                    hand.remove(discard)

                    sql = "SELECT deck FROM rooms WHERE room_id = ?"
                    db.execute(sql, (room,))
                    deck = db.fetchone()[0]
                    deck = json.loads(deck)
                    hand.append(deck[0])
                    deck.pop(0)
                    sql = "UPDATE alco SET hand = ? WHERE id = ?"
                    dumped_hand = json.dumps(hand).encode('utf-8')
                    db.execute(sql, (dumped_hand, user,))
                    sql = "UPDATE rooms SET deck = ? WHERE room_id = ?"
                    deck = json.dumps(deck).encode("utf-8")
                    db.execute(sql, (deck, room,))

                    for i in range(len(hand)):
                        hand[i] = telebot.types.InputMediaPhoto(crd[str(hand[i]) + ".jpg"])
                    sql = "SELECT mediagroup, message, votedcards FROM alco WHERE id = ?"
                    db.execute(sql, (user,))
                    media_id, old_message_id, voted_cards = db.fetchall()[0]
                    print(media_id, old_message_id, voted_cards, "media_id, old_message_id, voted_cards")
                    print(players_amount, "PLAYERS AMOUNT")
                    for i in range(players_amount):
                        #YUHFVGIJGILJHLKFUHJFKJHGJGJKKJGJHKJHFJGHKHLJGKFDFYGUHIJOKJHLGKFGJHJHLKJ:JFGDHFJKLK:KJHJGJHLKJ:
                        bot.delete_message(chat_id=user, message_id=voted_cards + i)
                    for i in range(6):
                        try:
                            bot.edit_message_media(media=hand[i], chat_id=user, message_id=media_id + i)
                        except:
                            pass
                    if queue == 1: #if user == new_current_player:
                        bot.edit_message_text(text=("Vote is done, your new score is:" + str(score)
                                              + "\n\n" + "Your turn, play card!"),
                                              chat_id=new_current_player, message_id=int(old_message_id),
                                              reply_markup=inmarkup_play())
                    else:
                        print(user, int(old_message_id), "INT OLD M")
                        bot.edit_message_text(text=("Vote is done, your new score is:" + str(score)
                                              + "\n\n" + "Wait for current player to play card"),
                                              chat_id=user, message_id=int(old_message_id))

                sql = "UPDATE rooms SET (is_started, current_player, deck) = (?, ?, ?) WHERE room_id = ?"
                db.execute(sql, (1, new_current_player, deck, room,))
                sql = "SELECT deck FROM rooms WHERE room_id = ?"
                db.execute(sql, (room,))
                deck = json.loads(db.fetchone()[0])
                for item in discards:
                    deck.append(item)
                random.shuffle(deck)
                deck = json.dumps(deck).encode("utf-8")
                sql = "UPDATE rooms SET deck = ? WHERE room_id = ?"
                db.execute(sql, (deck, room,))
                db.close()
                return "vote_done"
            else:
                message = bot.edit_message_text(text="Your vote accepted, wait for others",
                                                chat_id=user_id, message_id=message_id)
                sql = "UPDATE alco SET message = ? WHERE id = ?"
                db.execute(sql, (message.message_id, user_id))
                return "vote_done"
        else:
            message = bot.edit_message_text(chat_id=user_id, text="You can`t choose your own card",
                                            message_id=message_id, reply_markup=inmarkup_vote(players_amount))
            sql = "UPDATE alco SET message = ? WHERE id = ?"
            db.execute(sql, (message.message_id, user_id))
            db.close()
            return "error_vote_your_card"
    else:
        bot.send_message(user_id, "you are not allowed to vote now")
        db.close()
        return "error_vote"
