import psycopg2 as postgresql
from config import POSTGRESQL_LOGIN


class DataBaseManager:
    def __init__(self, creds):
        self.conn = postgresql.connect(**creds)

    def find_client(self, username):  # deprecated
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

    def create_service_data(self, username, password, role):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Service_data\"( service_data_login, service_data_password,"
                        "service_data_role) VALUES (%s, %s, %s)", (username, password, role))
            self.conn.commit()

    def select_all(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM public.\"Service_data\""
                        "ORDER BY service_data_id ASC")
            result = cur.fetchall()
        return result