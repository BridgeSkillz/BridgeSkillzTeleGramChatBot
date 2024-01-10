import sqlite3
from chatBot.constants import PROJECT_ROOT_PATH


class AlterDatabase:
    def __init__(self):
        self.con = sqlite3.connect(PROJECT_ROOT_PATH / "DB" / "Database.sqlite")
        self.cur = self.con.cursor()

    def add_field(self):
        self.cur.execute(
            """
            ALTER TABLE CHATHISTORY
            ADD is_question BOOLEAN DEFAULT 0
        """
        )
        self.con.commit()


# Create an instance of the AlterDatabase class

alter_db = AlterDatabase()
alter_db.add_field()

print("BridgeSkillz - DATABASE UPDATED SUCCESSFULLY")