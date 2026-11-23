import sqlite3 as sql
from datetime import datetime
from pathlib import Path




class BotBD:
    def __init__(self):
        try: self.conn = sql.connect("/data/Notifier.db")
        except: self.conn = sql.connect("Notifier.db")
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
                Date   TEXT    NOT NULL,              -- ISO 8601 (YYYY-MM-DD)
                Status INTEGER NOT NULL DEFAULT 0
                       CHECK(Status IN (0, 1)),
                FOREIGN KEY(UserId) REFERENCES Users(Id) ON DELETE CASCADE
            )
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_userid
                ON Notifications(UserId)
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Reminders (
                NotificationId INTEGER NOT NULL,
                Kind           TEXT    NOT NULL,      -- '3d' | '1d' | '0d' | 'overdue'
                SentAt         TEXT    NOT NULL,
                PRIMARY KEY (NotificationId, Kind),
                FOREIGN KEY(NotificationId) REFERENCES Notifications(Id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    def add_user(self, user_id, name):
        params = (user_id, name)
        self.cur.execute("INSERT OR IGNORE INTO Users(Id, Name) VALUES(?, ?)", params)
        self.conn.commit()

    def add_notification(self, user_id, data, date):
        if hasattr(date, "isoformat"):
            date = date.isoformat()[:10]
        params = (user_id, data, str(date))
        self.cur.execute("INSERT INTO Notifications(UserId, Data, Date) VALUES(?, ?, ?)", params)
        self.conn.commit()

    def get_user_notifications(self, user_id):
        params = (user_id,)
        return self.cur.execute(
            "SELECT Id, Data, Date, Status FROM Notifications WHERE UserId = ?",
            params,
        ).fetchall()

    def get_pending_notifications(self):
        """Активные задачи для планировщика напоминаний."""
        return self.cur.execute(
            "SELECT Id, UserId, Data, Date FROM Notifications WHERE Status = 0"
        ).fetchall()

    def get_sent_reminders(self) -> dict[int, set[str]]:
        """Какие напоминания уже отправлены: {NotificationId: {'3d', '1d', ...}}."""
        reminders: dict[int, set[str]] = {}
        for notification_id, kind in self.cur.execute(
            "SELECT NotificationId, Kind FROM Reminders"
        ):
            reminders.setdefault(notification_id, set()).add(kind)
        return reminders

    def mark_reminder_sent(self, notification_id, kind):
        self.cur.execute(
            "INSERT OR IGNORE INTO Reminders(NotificationId, Kind, SentAt) "
            "VALUES (?, ?, ?)",
            (notification_id, kind, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def change_status(self, task_id, status=1):
        params = (status, task_id,)
        self.cur.execute("UPDATE Notifications SET Status = ? WHERE Id = ?", params)
        self.conn.commit()

    def get_task_status(self, task_id):
        params = (task_id,)
        return self.cur.execute("SELECT Status FROM Notifications WHERE Id = ?", params).fetchone()

    def is_user_in_bd(self, user_id):
        params = (user_id,)
        return self.cur.execute("SELECT * FROM Users WHERE Id = ?", params).fetchone() is not None

    def get_task_by_id(self, task_id):
        params = (task_id,)
        return self.cur.execute("SELECT Data, Date, Status FROM Notifications WHERE Id = ?", params).fetchone()

    def close_connection(self):
        self.conn.close()
