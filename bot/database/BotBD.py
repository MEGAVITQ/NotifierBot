import sqlite3 as sql

class BotBD:
    def __init__(self):
        self.conn = sql.connect("Notifier.db")
        self.cur = self.conn.cursor()

    def create_tables(self):
        self.cur.execute("PRAGMA foreign_keys = ON")

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                Id   TEXT PRIMARY KEY,
                Name TEXT NOT NULL
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Notifications (
                Id     INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId TEXT    NOT NULL,
                Data   TEXT    NOT NULL,
                Date   TEXT    NOT NULL,              -- ISO 8601
                Status INTEGER NOT NULL DEFAULT 0
                       CHECK(Status IN (0, 1)),
                FOREIGN KEY(UserId) REFERENCES Users(Id) ON DELETE CASCADE
            )
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_userid
                ON Notifications(UserId)
        """)

        self.conn.commit()

    def add_user(self, user_id, name):
        params = (user_id, name)
        self.cur.execute("INSERT INTO Users VALUES(?, ?)", params)
        self.conn.commit()

    def add_notification(self, user_id, data, date):
        params = (user_id, data, date)
        self.cur.execute("INSERT INTO Notifications(UserId, Data, Date) VALUES(?, ?, ?)", params)
        self.conn.commit()

    def get_user_notifications(self, user_id):
        params = (user_id,)
        return self.cur.execute("SELECT Data, Date FROM Notifications WHERE UserId = ?", params).fetchall()

    def change_status(self, user_id, status = 1):
        params = (user_id, status,)
        self.cur.execute("UPDATE Notifications SET Status = ? WHERE UserId = ?", params)
        self.conn.commit()

    def is_user_in_bd(self, user_id):
        params = (user_id,)
        return self.cur.execute("SELECT * FROM Users WHERE Id = ?", params).fetchone() is not None

    def close_connection(self):
        self.conn.close()