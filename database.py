 # Copyright (C) <2020>  <Michele Viotto>
import mysql.connector


class Covid19Database():
    def __init__(self, config):
        self.config = config

    def add_user(self, user_id):
        cursor = self.db.cursor(prepared=True)
        select_query = "select * from users where user_id = %s"
        select_params = (user_id,)
        cursor.execute(select_query, select_params)
        query_result = cursor.fetchall()
        if not query_result:
            insert_query = "insert into users (user_id) values (%s)"
            insert_params = (user_id,)
            cursor.execute(insert_query, insert_params)
            self.db.commit()

        cursor.close()

    def remove_user(self, user_id):
        cursor = self.db.cursor(prepared=True)
        delete_query = "delete from users where user_id = %s"
        delete_params = (user_id,)
        cursor.execute(delete_query, delete_params)
        self.db.commit()

        cursor.close()

    def set_setting(self, user_id, setting, value):
        cursor = self.db.cursor(prepared=True)
        update_query = "update users set " + setting + " = %s where user_id = %s"
        update_params = (value, user_id)
        cursor.execute(update_query, update_params)
        self.db.commit()

        cursor.close()

    def get_setting(self, user_id, setting):
        cursor = self.db.cursor(prepared=True)
        select_query = "select " + setting + " from users where user_id = %s"
        select_params = (user_id,)
        cursor.execute(select_query, select_params)
        value = cursor.fetchone()[0]

        cursor.close()
        return value

    def is_admin(self, user_id):
        cursor = self.db.cursor(prepared=True)
        select_query = "select * from admins where user_id = %s"
        select_params = (user_id,)
        cursor.execute(select_query, select_params)
        if cursor.fetchone():
            return True

        return False  # user_id is not admin

    def get_users(self):
        cursor = self.db.cursor(prepared=True)
        select_query = "select * from users"
        cursor.execute(select_query)

        return cursor.fetchall()


    def init(self):
        self.db = mysql.connector.connect(
            host=self.config['host'],
            user=self.config['username'],
            passwd=self.config['password'],
            database=self.config['database']
        )
