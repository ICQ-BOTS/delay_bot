from apscheduler.schedulers.blocking import BlockingScheduler
from bot.bot import Bot
import database
import config
from datetime import datetime
import pytz

bot = Bot(token=config.MAIN_TOKEN)

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour="*", minute="*")
def date_job():
    time = datetime.strftime(datetime.now(tz=pytz.timezone('Europe/Moscow')), "%d.%m.%Y %H:%M")
    print(time)
    posts = database.get_posts(time)
    print(posts)
    if posts:
        for post in posts:
            post = list(post)
            if post[2]:
                if "voice" in post[2]:
                    bot.send_voice(chat_id=post[5], file_id=post[2][5:])
                else: 
                    if post[1] == "":
                        bot.send_file(chat_id=post[5], file_id=post[2])
                    else:
                        bot.send_file(chat_id=post[5], caption=post[1], file_id=post[2])
            else:
                bot.send_text(chat_id=post[5], text=post[1])
            database.update_post(post[0])


@sched.scheduled_job('cron', hour="*", minute=0)
def hour_job():
    time = int(datetime.strftime(datetime.now(tz=pytz.timezone('Europe/Moscow')), "%H"))
    posts = database.get_posts(time)
    if posts:
        for post in posts:
            post = list(post)
            if post[2]:
                if "voice" in post[2]:
                    bot.send_voice(chat_id=post[5], file_id=post[2][5:])
                else: 
                    if post[1] == "":
                        bot.send_file(chat_id=post[5], file_id=post[2])
                    else:
                        bot.send_file(chat_id=post[5], caption=post[1], file_id=post[2])
            else:
                bot.send_text(chat_id=post[5], text=post[1])
            database.update_post(post[0])

if __name__ == '__main__':
    sched.start()

