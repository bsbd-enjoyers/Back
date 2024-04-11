import psycopg2 as postgre
from config import POSTGRE_LOGIN


class DBmanager:
    def __init__(self):
        self.conn = None
        try:
            self.conn = postgre.connect(**POSTGRE_LOGIN)
            self.cursore = conn.
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    def find_login(self, username):
        return ()
