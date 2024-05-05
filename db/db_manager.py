import psycopg2 as postgresql
from dto.auth import RegisterData
from dto.order import Order


class DataBaseManager:
    def __init__(self, creds):
        self.conn = postgresql.connect(**creds)

    def find_account(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT service_data_login, service_data_password, service_data_role, service_data_id"
                        " FROM public.\"Service_data\" WHERE service_data_login=%s", (username,))
            result = cur.fetchone()
        return result

    def create_service_data(self, userdata: RegisterData):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Service_data\"( service_data_login, service_data_password,"
                        "service_data_role) VALUES (%s, %s, %s) RETURNING service_data_id",
                        (userdata.username, userdata.password, userdata.role.value))
            userdata.add_service_data_id(cur.fetchone()[0])
            self.conn.commit()

    def create_client_profile(self, userdata: RegisterData):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Client\" (client_full_name, client_email, client_phone, "
                        "client_service_id) VALUES (%s, %s, %s, %s)",
                        (userdata.fullname, userdata.email, userdata.phone, userdata.service_data_id))
            self.conn.commit()

    def create_master_profile(self, userdata: RegisterData):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Master\"(master_full_name, master_email, master_phone, "
                        "master_detailed_info, master_service_id) VALUES (%s, %s, %s, %s, %s) RETURNING master_id",
                        (userdata.fullname, userdata.email, userdata.phone, userdata.about, userdata.service_data_id))
            userdata.add_master_id(cur.fetchone()[0])
            print("INSERT INTO public.\"Skill\"(master_id, skill_type, skill_description) VALUES " + ",".join(
                [""] * len(userdata.skills)))
            cur.execute("INSERT INTO public.\"Skill\"(master_id, skill_type, skill_description) "
                        "VALUES " + ",".join(["%s"] * len(userdata.skills)),
                        userdata.get_skill_tuples())
            self.conn.commit()

    def get_service_id(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT service_data_id"
                        " FROM public.\"Service_data\" WHERE service_data_login=%s", (username,))
            result = cur.fetchone()[0]
        return result

    def get_client(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT client_id, client_full_name, client_email, client_phone "
                        "FROM public.\"Client\" JOIN public.\"Service_data\" ON "
                        "public.\"Service_data\".service_data_id=public.\"Client\".client_service_id Where "
                        "service_data_login=%s", (username,))
            result = cur.fetchone()
        return result

    def get_master(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT master_id, master_full_name, master_email, master_phone, master_detailed_info "
                        "FROM public.\"Master\" JOIN public.\"Service_data\" ON "
                        "public.\"Service_data\".service_data_id=public.\"Master\".master_service_id Where "
                        "service_data_login=%s",
                        (username,))
            result = cur.fetchone()
        return result

    def get_client_orders(self, client_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT order_id, order_deadline, order_totalcost, order_status, product_full_name, "
                        "product_client_description, product_master_specification FROM public.\"Order\" JOIN "
                        "public.\"Product\" ON public.\"Order\".product_id=public.\"Product\".product_id WHERE "
                        "client_id=%s", (client_id,))
            result = cur.fetchall()
        return result

    def get_master_orders(self, master_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT order_id, order_deadline, order_totalcost, order_status, product_full_name, "
                        "product_client_description, product_master_specification FROM public.\"Order\" JOIN "
                        "public.\"Product\" ON public.\"Order\".product_id=public.\"Product\".product_id WHERE "
                        "master_id=%s", (master_id,))
            result = cur.fetchall()
        return result

    def create_order(self, order: Order):
        pass

    def get_skills(self, master_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT skill_type, skill_description "
                        "FROM public.\"Skill\" WHERE master_id=%s", (master_id,))
            result = cur.fetchall()
        return result
