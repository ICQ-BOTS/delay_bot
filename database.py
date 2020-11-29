import sqlite3

database = 'database.sqlite'

def init_db():
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("""
    CREATE table user (
        id integer primary key,
        user_id text
    );
    """)
    cursor.execute("""
    CREATE table post (
        id integer primary key,
        text_post text,
        files text,
        status text,
        post_time text,
        public text
    );
    """)
    cursor.execute("""
    CREATE table last_post (
        id integer primary key,
        user_id text,
        post_id integer
    );
    """)
    cursor.execute("""
    CREATE table public (
        id integer primary key,
        user_id text,
        public_id text,
        name text
    );
    """)
    connect.close()

def delete_public(user_id,public_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("DELETE FROM public WHERE user_id='"+str(user_id)+"' and public_id='"+str(public_id)+"'")
    connect.commit()
    connect.close()

def delete_post(post_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("DELETE FROM post WHERE id='"+str(post_id)+"'")
    connect.commit()
    connect.close()

def get_queue_posts(public_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM post WHERE status='non_posted' and public='"+str(public_id)+"'")
    posts = cursor.fetchall()
    if posts:
        for i in range(0,len(posts)):
            posts[i] = list(posts[i])
    connect.close()
    return posts

def add_public(user_id,public,name):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM public")
    try:
        new_id = str(cursor.fetchall()[-1][0] + 1)
    except:
        new_id = 1
    cursor.execute("insert into public values ("+str(new_id)+",'"+user_id+"','"+public+"','"+name+"')")
    connect.commit()
    connect.close()
    return new_id

def get_public(user_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM public WHERE user_id='"+str(user_id)+"'")
    result = cursor.fetchall()
    connect.close()
    print(result)
    if result:
        for i in range(0,len(result)):
            result[i] = list(result[i])
    return result

def update_last_post(post_id,user_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM last_post WHERE user_id='"+user_id+"'")
    try:
        post = cursor.fetchall()[0][0]
        cursor.execute("UPDATE last_post SET post_id="+str(post_id)+" where user_id='"+user_id+"'")
        connect.commit()
    except:
        cursor.execute("SELECT id FROM last_post")
        try:
            new_id = str(cursor.fetchall()[-1][0] + 1)
        except:
            new_id = 1
        cursor.execute("insert into last_post values ("+str(new_id)+",'"+user_id+"',"+str(post_id)+")")
        connect.commit()
    connect.close()

def get_last_post(user_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT post_id FROM last_post WHERE user_id='"+user_id+"'")
    post_id = cursor.fetchall()[-1][0]
    connect.close()
    return post_id

def add_new_post(data):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM post")
    try:
        new_id = str(cursor.fetchall()[-1][0] + 1)
    except:
        new_id = 1
    try:
        photo = data['parts'][0]["payload"]["fileId"]
        if data['parts'][0]["type"] == "voice":
            photo = "voice" + photo
        try: 
            text = data['parts'][0]["payload"]["caption"]
        except:
            text = ""
        cursor.execute("insert into post values ("+str(new_id)+",'"+text+"','"+photo+"','non_posted','null','public')")
    except:
        photo = ""
        cursor.execute("insert into post values ("+str(new_id)+",'"+data['text']+"','"+photo+"','non_posted','null','public')")
    connect.commit()
    connect.close()
    update_last_post(new_id,data["chat"]["chatId"])
    return new_id

def check_user(user_id):
    result = {}
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id='" + str(user_id)+"'")
    res = cursor.fetchall()
    connect.close()
    try:
        if res[0]:
            result["not_exist"] = False
            result["id"] = res[0][1]
    except:
        result["not_exist"] = True
    return result

def check_post(post_id):
    result = {}
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM post WHERE id='" + str(post_id)+"'")
    res = cursor.fetchall()
    connect.close()
    result["public"] = res[0][5]
    return result

def add_user(user_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM user")
    try:
        new_id = str(cursor.fetchall()[-1][0] + 1)
    except:
        new_id = 1
    cursor.execute("insert into user values ("+str(new_id)+",'"+str(user_id)+"')")
    connect.commit()
    connect.close()

def update_time(post_time,post_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("UPDATE post SET post_time='"+str(post_time)+"' where id="+str(post_id))
    connect.commit()
    connect.close()

def update_post(post_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("UPDATE post SET status='posted' where id="+str(post_id))
    connect.commit()
    connect.close()

def update_public(post_id,public):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("UPDATE post SET public='"+public+"' where id="+str(post_id))
    connect.commit()
    connect.close()

def get_posts(time):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM post WHERE status='non_posted' and post_time='"+str(time)+"'")
    posts = cursor.fetchall()
    connect.close()
    return posts

def get_db(table):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM "+table)
    result = cursor.fetchall()
    connect.close()
    return result

if __name__ == '__main__': 
	init_db()