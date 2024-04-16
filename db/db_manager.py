import psycopg2 as postgre
from config import POSTGRE_LOGIN


class DataBaseManager:
    def __init__(self):
        self.conn = None
        try:
            self.conn = postgre.connect(**POSTGRE_LOGIN)
            self.cur = self.conn.cursor()
        except (postgre.DatabaseError, Exception) as error:
            print(error)

    def find_login(self, username):
        return ()
