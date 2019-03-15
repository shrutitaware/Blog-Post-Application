import sqlite3

conn = sqlite3.connect('blogdatabase.db')

c = conn.cursor()

c.execute("delete from users")
c.execute("delete from article")
c.execute("delete from comment")
c.execute("delete from tag_head")
c.execute("delete from tag_detail")

conn.commit()

conn.close()
