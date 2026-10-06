import sqlite3
import os

class Databse:
    def __init__(self):
        self.con = sqlite3.connect(os.path.join("data", "webapps.db"))
        self.cur = self.con.cursor()

        self.create_tables()

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS web_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL CHECK(length(app_name) <= 64),
            url TEXT NOT NULL CHECK(length(url) <= 2000),
            shortcut TEXT NOT NULL CHECK(length(shortcut) <= 2500),
            tag TEXT CHECK(length(tag) <= 50)
        );
        """
        self.cur.execute(query)
        self.con.commit()

    def get_all(self):
        query = """
        SELECT id, app_name, url, shortcut, tag FROM web_apps
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get(self, id: int):
        query = """
            SELECT id, app_name, url, shortcut, tag FROM web_apps
            WHERE id = ?
        """
        self.cur.execute(query, (id,))
        return self.cur.fetchone()

    def add(self, app_name: str, url: str, shortcut: str, tag: str | None=None) -> int | None:
        query = """
            INSERT INTO web_apps (app_name, url, shortcut, tag)
            VALUES (?, ?, ?, ?)
        """
        self.cur.execute(query, (app_name, url, shortcut, tag))
        self.con.commit()
        return self.cur.lastrowid

    def remove(self, id: int):
        query = """
            DELETE FROM web_apps
            WHERE id = ?
        """
        self.cur.execute(query, (id,))
        self.con.commit()

    def update(self, id: int, app_name=None, url=None, shortcut=None, **kwargs):
        """
        """
        fields = []
        values = []
        if app_name is not None:
            fields.append("app_name = ?")
            values.append(app_name)
        if url is not None:
            fields.append("url = ?")
            values.append(url)
        if shortcut is not None:
            fields.append("shortcut = ?")
            values.append(shortcut)
        if "tag" in kwargs:
            fields.append("tag = ?")
            values.append(kwargs["tag"])
        if not fields:
            return
        values.append(id)
        query = f"""
            UPDATE web_apps
            SET {", ".join(fields)}
            WHERE id = ?
        """
        self.cur.execute(query, values)
        self.con.commit()

    def get_tags(self):
        query = """
            SELECT DISTINCT tag
            FROM web_apps
            WHERE tag IS NOT NULL
            AND tag != ''
        """
        self.cur.execute(query)
        return [row[0] for row in self.cur.fetchall()]

    def clear_all(self):
        query = """
            DELETE FROM web_apps
        """
        self.cur.execute(query)
        self.con.commit()

if __name__ == "__main__":
    db = Databse()
    db.get_all()
