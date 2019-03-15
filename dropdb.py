import sqlite3

conn = sqlite3.connect('blogdatabase.db')

c = conn.cursor()

c.execute("drop table users")
c.execute("drop table article")
c.execute("drop table comment")
c.execute("drop table tag_head")
c.execute("drop table tag_detail")

conn.commit()

conn.close()
