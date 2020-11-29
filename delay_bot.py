from bot.bot import Bot
from bot.filter import Filter
from bot.handler import (BotButtonCommandHandler, DefaultHandler,
                         HelpCommandHandler, MessageHandler,
                         StartCommandHandler)

import config
from server import (but_deletepost, but_deletepublic, but_post, but_public,
                    but_queuepublic, delete_public, main_message, queue_posts,
                    setpublic_cm, settime_cm)

bot = Bot(token=config.MAIN_TOKEN)
bot.dispatcher.add_handler(StartCommandHandler(
    callback=main_message
))
bot.dispatcher.add_handler(HelpCommandHandler(
    callback=main_message
))

bot.dispatcher.add_handler(MessageHandler(
    callback=setpublic_cm,
    filters=Filter.regexp('^\/setpublic')
))

bot.dispatcher.add_handler(MessageHandler(
    callback=settime_cm,
    filters=Filter.regexp('^\/settime')
))

bot.dispatcher.add_handler(MessageHandler(
    callback=delete_public,
    filters=Filter.regexp('^\/delete')
))

bot.dispatcher.add_handler(MessageHandler(
    callback=queue_posts,
    filters=Filter.regexp('^\/queue')
))

bot.dispatcher.add_handler(DefaultHandler(
    callback=queue_posts
))

bot.dispatcher.add_handler(BotButtonCommandHandler(
    callback=but_public,
    filters=Filter.callback_data_regexp(r'public')
))

bot.dispatcher.add_handler(BotButtonCommandHandler(
    callback=but_post,
    filters=Filter.callback_data_regexp(r'post')
))

bot.dispatcher.add_handler(BotButtonCommandHandler(
    callback=but_deletepublic,
    filters=Filter.callback_data_regexp(r'deletepublic')
))

bot.dispatcher.add_handler(BotButtonCommandHandler(
    callback=but_deletepost,
    filters=Filter.callback_data_regexp(r'deletepost')
))

bot.dispatcher.add_handler(BotButtonCommandHandler(
    callback=but_queuepublic,
    filters=Filter.callback_data_regexp(r'queuepublic')
))

bot.start_polling()
bot.idle()
