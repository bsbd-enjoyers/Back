from db.db_manager import DataBaseManager
from dto.order import Order


class Update:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    def add_order(self, order: Order):
        self.DB_manager.create_order(order)

    def change_order_status(self):
        pass
