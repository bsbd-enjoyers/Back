import psycopg2 as postgresql
from dto.auth import RegisterData, Role
from dto.order import UpdateOrder, OrderStatus
from dto.simple import ManageEntity


class QueryResult:
    Success = "Query was executed"
    Fail = "Query Failed"


class DataBaseManager:
    def __init__(self, creds):
        self.conn = postgresql.connect(**creds)

    @staticmethod
    def handle_sql_query(request):
        def wrapper(self, *args, **kwargs):
            value = None
            try:
                value = request(self, *args, **kwargs)
            except Exception as e:
                print("Exception during Query:")
                print(e)
                self.conn.rollback()
                return None, QueryResult.Fail
            self.conn.commit()
            return value, QueryResult.Success

        return wrapper

    @handle_sql_query
    def find_account(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT service_data_login, service_data_password, service_data_role, service_data_id, "
                        "service_data_banned FROM public.\"Service_data\" WHERE service_data_login=%s", (username,))
            result = cur.fetchone()
        return result

    @handle_sql_query
    def create_account(self, userdata: RegisterData):
        self.__create_service_data(userdata)
        if userdata.role == Role.Master:
            self.__create_master_profile(userdata)
        else:
            self.__create_client_profile(userdata)

    def __create_service_data(self, userdata: RegisterData):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Service_data\"( service_data_login, service_data_password,"
                        "service_data_role) VALUES (%s, %s, %s) RETURNING service_data_id",
                        (userdata.username, userdata.password, userdata.role.value))
            userdata.add_service_data_id(cur.fetchone()[0])

    def __create_client_profile(self, userdata: RegisterData):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Client\" (client_full_name, client_email, client_phone, "
                        "client_service_id) VALUES (%s, %s, %s, %s)",
                        (userdata.fullname, userdata.email, userdata.phone, userdata.service_data_id))

    def __create_master_profile(self, userdata: RegisterData):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Master\"(master_full_name, master_email, master_phone, "
                        "master_detailed_info, master_service_id) VALUES (%s, %s, %s, %s, %s) RETURNING master_id",
                        (userdata.fullname, userdata.email, userdata.phone, userdata.about, userdata.service_data_id))
            userdata.add_master_id(cur.fetchone()[0])
            cur.execute("INSERT INTO public.\"Skill\"(master_id, skill_type, skill_description) "
                        "VALUES " + ",".join(["%s"] * len(userdata.skills)),
                        userdata.get_skill_tuples())

    @handle_sql_query
    def get_service_id(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT service_data_id"
                        " FROM public.\"Service_data\" WHERE service_data_login=%s", (username,))
            result = cur.fetchone()[0]
        return result

    @handle_sql_query
    def get_client(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT client_id, client_full_name, client_email, client_phone "
                        "FROM public.\"Client\" JOIN public.\"Service_data\" ON "
                        "public.\"Service_data\".service_data_id=public.\"Client\".client_service_id Where "
                        "service_data_login=%s", (username,))
            result = cur.fetchone()
        return result

    @handle_sql_query
    def get_master(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT master_id, master_full_name, master_email, master_phone, master_detailed_info "
                        "FROM public.\"Master\" JOIN public.\"Service_data\" ON "
                        "public.\"Service_data\".service_data_id=public.\"Master\".master_service_id Where "
                        "service_data_login=%s",
                        (username,))
            result = cur.fetchone()
        return result

    @handle_sql_query
    def get_client_orders(self, client_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT order_id, order_deadline, master_id, client_id, order_client_cost, order_master_cost, "
                        "order_status, product_name, product_type, product_client_description, "
                        "product_master_specification FROM public.\"Order\" JOIN public.\"Product\" ON "
                        "public.\"Order\".product_id=public.\"Product\".product_id WHERE client_id=%s", (client_id,))
            result = cur.fetchall()
        return result

    @handle_sql_query
    def get_master_orders(self, master_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT order_id, order_deadline, master_id, client_id, order_client_cost, order_master_cost, "
                        "order_status, product_name, product_type, product_client_description, "
                        "product_master_specification FROM public.\"Order\" JOIN public.\"Product\" ON "
                        "public.\"Order\".product_id=public.\"Product\".product_id WHERE master_id=%s", (master_id,))
            result = cur.fetchall()
        return result

    @handle_sql_query
    def create_order(self, order: UpdateOrder):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO public.\"Product\" (product_type, product_name, "
                        "product_client_description, product_master_specification)"
                        "VALUES (NULL, %s, %s, NULL) RETURNING product_id", (order.create.name, order.create.desc))
            product_id = cur.fetchone()[0]
            cur.execute("INSERT INTO public.\"Order\"(client_id, product_id, "
                        "order_deadline, order_client_cost, order_status) VALUES (%s, %s, %s, %s, %s)",
                        (order.jwt_data.id, product_id, order.create.deadline, order.create.cost, order.create.status))

    @handle_sql_query
    def get_skills(self, master_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT skill_type, skill_description "
                        "FROM public.\"Skill\" WHERE master_id=%s", (master_id,))
            result = cur.fetchall()
        return result

    @handle_sql_query
    def get_order_status(self, order: UpdateOrder) -> OrderStatus:
        with self.conn.cursor() as cur:
            cur.execute("SELECT order_status FROM public.\"Order\" WHERE order_id=%s",
                        (order.order_id,))
            result = cur.fetchone()[0]
        return OrderStatus(result)

    @handle_sql_query
    def set_client_submit(self, order: UpdateOrder):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE public.\"Order\" SET  order_status='accepted' WHERE order_id=%s",
                        (order.order_id,))

    @handle_sql_query
    def reset_order_created(self, order: UpdateOrder):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE public.\"Order\" SET  order_status='created', order_master_cost=NULL, master_id=NULL "
                        "WHERE order_id=%s RETURNING product_id",
                        (order.order_id,))
            product_id = cur.fetchone()[0]
            cur.execute("UPDATE public.\"Product\" SET product_type=NULL, product_master_specification=NULL "
                        "WHERE product_id=%s", (product_id,))

    @handle_sql_query
    def set_master_info_order(self, order: UpdateOrder):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE public.\"Order\" SET  order_status='updated', order_master_cost=%s, master_id=%s "
                        "WHERE order_id=%s RETURNING product_id",
                        (order.update.cost, order.jwt_data.id, order.order_id,))
            product_id = cur.fetchone()[0]
            cur.execute("UPDATE public.\"Product\" SET product_type=%s, product_master_specification=%s "
                        "WHERE product_id=%s", (order.update.product_type, order.update.mater_desc, product_id,))

    @handle_sql_query
    def search_order(self, substr: str):
        substr = substr.lower()
        with self.conn.cursor() as cur:
            cur.execute("SELECT order_id, order_deadline, master_id, client_id, order_client_cost, order_master_cost, "
                        "order_status, product_name, product_type, product_client_description, "
                        "product_master_specification FROM public.\"Order\" JOIN public.\"Product\" ON "
                        "public.\"Order\".product_id=public.\"Product\".product_id WHERE "
                        "public.\"Order\".order_status='created' AND (LOWER(public.\"Product\".product_name) ~ %s OR "
                        "LOWER(public.\"Product\".product_client_description) ~ %s)", (substr, substr))
            result = cur.fetchall()
        return result

    @handle_sql_query
    def delete_order(self, delete_info: ManageEntity):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM public.\"Order\" WHERE order_id=%s AND client_id=%s RETURNING product_id",
                        (delete_info.id, delete_info.jwt_data.id))
            product_id = cur.fetchall()
            if len(product_id) != 1:
                raise RuntimeError(f"Bad Number of records was deleted {len(product_id)}")
            cur.execute("DELETE FROM public.\"Product\" WHERE product_id=%s",
                        (product_id[0][0],))

    @handle_sql_query
    def ban_account(self, ban_info: ManageEntity):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE public.\"Service_data\" SET service_data_banned=true WHERE service_data_role=%s AND "
                        "service_data_id=%s RETURNING service_data_id",
                        (ban_info.entity.value, ban_info.id,))
            banned_id = cur.fetchall()
            if len(banned_id) != 1:
                raise RuntimeError(f"Bad Number of records was deleted {len(banned_id)}")

    @handle_sql_query
    def search_clients(self, substr: str):
        substr = substr.lower()
        with self.conn.cursor() as cur:
            cur.execute("SELECT client_id, client_full_name, client_email, client_phone "
                        "FROM public.\"Client\" WHERE LOWER(client_full_name) ~ %s OR LOWER(client_email) ~ %s",
                        (substr, substr,))
            result = cur.fetchall()
        return result

    @handle_sql_query
    def search_masters(self, substr: str):
        substr = substr.lower()
        with self.conn.cursor() as cur:
            cur.execute("SELECT master_id, master_full_name, master_email, master_phone, master_detailed_info "
                        "FROM public.\"Master\"  Where LOWER(master_full_name) ~ %s OR LOWER(master_email) ~ %s OR "
                        "LOWER(master_detailed_info) ~ %s", (substr, substr, substr,))
            result = cur.fetchall()
        return result


