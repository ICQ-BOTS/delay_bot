from bot.bot import Bot
from bot.handler import MessageHandler,BotButtonCommandHandler
import database
import json
import re


def init_user(func):
    def wrapper(*args, **kwargs):
        user_info = database.check_user(kwargs['event'].data["from"]["userId"])
        if user_info["not_exist"]:
            database.add_user(kwargs['event'].data["from"]["userId"])
            user_info = database.check_user(kwargs['event'].data["from"]["userId"])
        func(*args, **kwargs)
    return wrapper


@init_user
def setpublic_cm(bot, event):
    set_public(bot, event.data, event.data["text"][11:])


@init_user
def settime_cm(bot, event):
    update_time(bot, event.data, event.data["text"][9:])



@init_user
def main_message(bot, event):
    message = """
    Привет!

Этот бот поможет вам публиковать посты на ваших каналах в определенные дату и время.

1. Для начала укажите канал, в котором необходимо будет сделать публикацию. Используй для этого команду /setpublic *id_паблика* *название*

id паблика можно найти в конце ссылки вашего чата https://icq.im/*********

Например: /setpublic icqchannels Каналы ICQ

Если у вас несколько каналов, то поочередно укажите их боту

2. Добавьте этого бота в указанные каналы и дайте права администратора.

3. Бот готов к работе.

⏳Для того, чтобы создать отложенный пост просто отправьте мне его. Я могу опубликовать текст, картинку или картинку с подписью.

Доступные команды:

/setpublic id_паблика название - Добавить новый паблик
/settime dd.mm.yyyy hh:mm - Установить время для последнего поста
/delete - Удалить паблик
/queue - Проверить очередь постов
/help - Помощь"""
    bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)


@init_user
def queue_posts(bot, event):
    data = event.data
    inline_keyboard_markup = []
    publics = database.get_public(data["chat"]["chatId"])
    for public in publics:
        if public[3] == "":
            public[3] = public[2]
        inline_keyboard_markup.append([{"text": public[3], "callbackData": "func_queuepublic_"+public[2]}])
    if publics == []:
        message = "Сначала добавь паблики командой /setpublic id_паблика название"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        return
    message = "Выбери паблик, для которого хочешь проверить посты в очереди"
    bot.send_text(chat_id=data["chat"]["chatId"], text=message, inline_keyboard_markup=json.dumps(inline_keyboard_markup))


@init_user
def delete_public(bot, event):
    data = event.data
    inline_keyboard_markup = []
    publics = database.get_public(data["chat"]["chatId"])
    for public in publics:
        if public[3] == "":
            public[3] = public[2]
        inline_keyboard_markup.append([{"text": public[3], "callbackData": "func_deletepublic_"+public[2]}])
    if publics == []:
        message = "Сначала добавь паблики командой /setpublic id_паблика название"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        return
    message = "Опасная зона!\n\nВыбери паблик, который хочешь удалить из своего списка"
    bot.send_text(chat_id=data["chat"]["chatId"], text=message, inline_keyboard_markup=json.dumps(inline_keyboard_markup))


def update_time(bot,data,text):
    post_id = database.get_last_post(data["chat"]["chatId"])
    public = database.check_post(post_id)["public"]
    is_admin = check_admin(bot,data["chat"]["chatId"],public)
    if is_admin:
        text_arr = text.split(" ")
        date_post = text_arr[0]
        time_post = text_arr[1]
        if re.match(r'^(0?[1-9]|[12][0-9]|3[01])[.](0?[1-9]|1[012])[.]\d{4}$', date_post) and re.match(r'(2[0-3]|[0-1]\d):[0-5]\d', time_post): 
            database.update_time(text,post_id)
            message = "Время и даты публикации успешно установлены на "+text
            bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        else:
            message = "Некорректный формат даты и времени пришли данные в формате /settime dd.mm.yyyy hh:mm"
            bot.send_text(chat_id=data["chat"]["chatId"], text=message)
    else:
        message = "Вы не являетесь администратором данного сообщества"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def set_public(bot,data,text):
    text_arr = text.split(" ")
    if text_arr[0]:
        if re.match(r'http', text_arr[0]):
            text_arr[0] = text_arr[0].split("/")[-1]
        text = ""
        for i in range(1,len(text_arr)):
            text += text_arr[i] + " "
        database.add_public(data["chat"]["chatId"],text_arr[0],text)
        message = "Паблик успешно добавлен"
    else:
        message = "Короткое сообщение, используй /setpublic id_паблика название"
    bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def add_post(bot, event):
    data = event.data
    new_id = database.add_new_post(data)
    message = "Твой пост был успешно добавлен, выбери чат в который нужно отправить данный пост"
    inline_keyboard_markup = []
    publics = database.get_public(data["chat"]["chatId"])
    for public in publics:
        if public[3] == "":
            public[3] = public[2]
        inline_keyboard_markup.append([{"text": public[3], "callbackData": "func_public_"+new_id+"_"+public[2]}])
    if publics == []:
        message = "Сначала добавь паблики командой /setpublic id_паблика название"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        return
    bot.send_text(chat_id=data["chat"]["chatId"], text=message, inline_keyboard_markup=json.dumps(inline_keyboard_markup))


def check_admin(bot,user_id,public):
    try:
        admins = bot.get_chat_admins(chat_id=public).json()['admins']
    except:
        message = "Дай боту права администратора в чате, чтобы он мог проверить что это твой паблик"
        bot.send_text(chat_id=user_id, text=message)
        return
    is_admin = False
    for i in admins:
        if user_id == i["userId"]:
            is_admin = True
            break
    return is_admin


def set_time(bot,data,post_id,public):
    is_admin = check_admin(bot,data["message"]["chat"]["chatId"],public)
    if is_admin == True:
        database.update_public(post_id,public)
        message = "А теперь выбери время публикации в следующие 24 часа по мск или установи любое время в будущем командой /settime dd.mm.yyyy hh:mm"
        inline_keyboard_markup = []
        hour = 0
        for i in range(0,6):
            inside_arr = []
            for j in range(0,4):
                inside_arr.append({"text": str(hour)+".00", "callbackData": "func_post_"+str(hour)+"_"+str(post_id)})
                hour += 1
            inline_keyboard_markup.append(inside_arr)
        bot.send_text(chat_id=data["message"]["chat"]["chatId"], text=message, inline_keyboard_markup=json.dumps(inline_keyboard_markup))
    elif is_admin == False:
        message = "Вы не являетесь администратором данного сообщества"
        bot.send_text(chat_id=data["message"]["chat"]["chatId"], text=message)


def but_public(bot, event):
    text = event.data["callbackData"].split("_")
    public = ""
    for i in range(3,len(text)-1):
        public += text[i] + "_"
    public += text[len(text)-1]
    set_time(bot, event.data, text[2], public) 


def but_post(bot, event):
    text = event.data["callbackData"].split("_")
    database.update_time(text[2], text[3])
    message = "Пост будет опубликован в ближайшие " + text[2] + ".00 по мск"
    bot.send_text(chat_id=event.data["message"]["chat"]["chatId"], text=message)


def but_deletepublic(bot, event):
    text = event.data["callbackData"].split("_")
    public = ""
    for i in range(2,len(text)-1):
        public += text[i] + "_"
    public += text[len(text)-1]
    database.delete_public(event.data["message"]["chat"]["chatId"],public)
    message = "Данный паблик успешно удален из твоего списка"
    bot.send_text(chat_id=event.data["message"]["chat"]["chatId"], text=message)


def but_deletepost(bot, event):
    text = event.data["callbackData"].split("_")
    database.delete_post(text[2])
    message = "Данный пост успешно удален из очереди"
    bot.send_text(chat_id=event.data["message"]["chat"]["chatId"], text=message)


def but_queuepublic(bot, event):
    text = event.data["callbackData"].split("_")
    public = ""
    for i in range(2,len(text)-1):
        public += text[i] + "_"
    public += text[len(text)-1]
    is_admin = check_admin(bot,event.data["message"]["chat"]["chatId"],public)
    if is_admin:
        posts = database.get_queue_posts(public)
        if posts:
            for post in posts:
                post = list(post)
                inline_keyboard_markup = []
                inline_keyboard_markup.append([{"text": "Удалить данный пост", "callbackData": "func_deletepost_"+str(post[0])}])
                if post[2]:
                    caption = post[1] + "\n\nВремя публикации: " + post[4]
                    bot.send_file(chat_id=event.data["message"]["chat"]["chatId"], caption=caption, file_id=post[2],inline_keyboard_markup=json.dumps(inline_keyboard_markup))
                else:
                    text = post[1] + "\n\nВремя публикации: " + post[4]
                    bot.send_text(chat_id=event.data["message"]["chat"]["chatId"], text=text,inline_keyboard_markup=json.dumps(inline_keyboard_markup))
        else: 
            message = "У тебя нет постов в очереди"
            bot.send_text(chat_id=event.data["message"]["chat"]["chatId"], text=message)
    else:
        message = "Вы не являетесь администратором данного сообщества"
        bot.send_text(chat_id=event.data["message"]["chat"]["chatId"], text=message)


