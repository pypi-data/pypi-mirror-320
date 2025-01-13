import pymysql.cursors
from typing import List

class DB:
    def  __init__(self, hostname: str = 'localhost', username: str = 'user', password: str = 'password', database: str = 'dbname'):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database
        self.connection = self.get_connection()

    def get_connection(self):
        return pymysql.connect(host=self.hostname,
                             user=self.username,
                             password=self.password,
                             database=self.database,
                             cursorclass=pymysql.cursors.DictCursor)

    def select(self, what: str = '*', table: str = 'request', where: str = None) -> tuple:
        where = f" where {where}" if where is not None else ''
        with self.connection.cursor() as cursor:
            sql = f"SELECT {what} from {table}{where}"
            print(sql)
            cursor.execute(sql)
            results = cursor.fetchall()
            print(results)
            return results

    def update(self, table: str = 'request', key: str = '', value: str or bool = '', where: str = None):
        where = f" where {where}" if where is not None else ''
        with self.connection.cursor() as cursor:
            sql = f'UPDATE {table} set {key} = "{value}"{where}'
            cursor.execute(sql)
            self.connection.commit()


    def update_many(self, kv_dict: dict, table: str = 'request', where: str = None):
        where = f" where {where}" if where is not None else ''
        with self.connection.cursor() as cursor:
            values = []
            for k in kv_dict.keys():
                values.append(f'{k} = "{kv_dict[k]}"')
            sql = f"UPDATE {table} set {', '.join(values)}{where}"
            cursor.execute(sql)
            self.connection.commit()


if __name__ == '__main__':
    db = DB()
    db.select(where='url = "https://www.youtube.com/watch?v=FilQhY2Pjq0"')
