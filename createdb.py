import sqlite3

conn = sqlite3.connect('blogdatabase.db')

c = conn.cursor()

c.execute(""" Create table if not exists users (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    password TEXT,
                    create_time DATETIME,
                    update_time DATETIME) """)

c.execute(""" Create table if not exists article (
                    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    email TEXT,
                    create_time DATETIME,
                    update_time DATETIME,
                    url TEXT,
                    FOREIGN KEY (email) REFERENCES users(email)) """)

c.execute(""" Create table if not exists comment (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comment_content TEXT,
                    email TEXT,
                    article_id INTEGER,
                    create_time DATETIME,
                    update_time DATETIME,
                    FOREIGN KEY (article_id) REFERENCES article(article_id)) """)

c.execute(""" Create table if not exists tag_head (
                    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_name TEXT,
                    tag_frequency TEXT,
                    create_time DATETIME,
                    update_time DATETIME) """)

c.execute(""" Create table if not exists tag_detail (
                    article_id INTEGER,
                    tag_id INTEGER NOT NULL REFERENCES tag_head(tag_id),
                    create_time DATETIME,
                    update_time DATETIME,
                    PRIMARY KEY(article_id,tag_id),
                    FOREIGN KEY (article_id) REFERENCES article(article_id)) """)

conn.commit()

conn.close()
