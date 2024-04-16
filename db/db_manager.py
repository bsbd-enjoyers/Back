import psycopg2 as postgresql
from config import POSTGRESQL_LOGIN


class DataBaseManager:
    def __init__(self):
        self.conn = postgresql.connect(**POSTGRESQL_LOGIN)

    def find_client(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT client_id, client_full_name, client_email, client_phone, client_login FROM "
                        "public.\"Client\" WHERE client_login=%s", (username,))
            result = cur.fetchone()
        return result

    def find_account(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT service_data_login, service_data_password, service_data_role"
                        " FROM public.\"Service_data\" WHERE service_data_login=%s", (username,))
            result = cur.fetchone()
        return result
