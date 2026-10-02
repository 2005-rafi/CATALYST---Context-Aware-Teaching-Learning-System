from backend.repositories.sqlite.database import db_connection

class BaseRepository:
    def _execute(self, sql: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False, commit: bool = True):
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            elif fetch_all:
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            else:
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
