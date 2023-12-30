import sqlite3
import os


class DBInstance(object):
    # Singleton pattern implementation
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(DBInstance, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.con = sqlite3.connect("local_data/Database.sqlite")
        self.cur = self.con.cursor()
        self.createTablesIfNotExist()

    def getConnection(self):
        return self.con

    def getCursor(self):
        return self.cur

    def createTablesIfNotExist(self):
        self.createChatHistoryStore()

    def createChatHistoryStore(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS CHATHISTORY (
                id INTEGER PRIMARY KEY,
                userid TEXT NOT NULL,
                username TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                createdon DATETIME DEFAULT CURRENT_TIMESTAMP
            ); """)

    def insertChatHistory(self, userid, username, role, content):
        self.cur.execute("""
            INSERT INTO CHATHISTORY (userid,username, role, content)
            VALUES (?, ?,?, ?)
        """, (userid, username, role, content))
        self.con.commit()

    def getChatHistoryByUserID(self, userid):
        self.cur.execute("""
            SELECT role, content FROM CHATHISTORY
            WHERE userid = ?
            ORDER BY createdon
        """, (userid,))

        # Fetching the data and converting it into a list of objects
        records = self.cur.fetchall()
        return [{"role": role, "content": content} for role, content in records]


# Create an instance of the DBInstance class
BRAIN = DBInstance()
