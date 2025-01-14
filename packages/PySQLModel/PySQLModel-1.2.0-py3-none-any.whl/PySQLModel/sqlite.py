"""
@Project:PgSqlModel
@File:sqlite.py
@Author:函封封
"""
import math
from contextlib import contextmanager
from typing import List, Tuple, Union


# sqlite操作
class SQLite():
    # 系统数据库
    __SYSTEM_TABLES = ["sqlite_master", "sqlite_sequence"]

    def __init__(self, connect=None, **kwargs):
        """
        DATABASES = {
            "database": "./demo.db"
        }
        """
        if connect is not None and hasattr(connect, "cursor"):
            self.connect = connect
        else:
            import sqlite3
            self.connect = sqlite3.connect(**kwargs)
        self.cursor = self.connect.cursor()  # 创建游标对象
        self.table_name = None  # 表名
        self.field_list = []  # 表字段
        self.where_sql = []  # 条件语句
        self.limit_sql = ""  # 分页
        self.group_sql = ""  # 分组
        self.order_sql = ""  # 排序
        self.sql = ""  # 执行 sql
        self.args = []  # 条件参数

    def close(self):
        """
        关闭数据库连接和游标。
        注意：此方法会关闭所有克隆对象共享的数据库连接。
        只有在确定所有相关操作都完成时才调用此方法。
        """
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
            self.cursor = None
        if hasattr(self, 'connect') and self.connect:
            self.connect.close()
            self.connect = None

    @contextmanager
    def atomic(self):
        """
        事务上下文管理器
        用法:
            with db.atomic():
                db.table("users").create(...)
                db.table("orders").create(...)
        """
        try:
            yield
            self.commit()
        except Exception as e:
            self.rollback()
            raise e

    def commit(self):
        """提交事务"""
        self.connect.commit()

    def rollback(self):
        """回滚事务"""
        self.connect.rollback()

    def show_table(self, show_system: bool = False) -> List[str]:
        """
        查询当前数据库中所有表
        :return: 返回一个列表
        """
        sql = "select name from sqlite_master where type='table'"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        table_list = []
        for row in rows:
            tb_name = row[0]
            if show_system is False and tb_name in self.__SYSTEM_TABLES:
                continue
            table_list.append(tb_name)
        return table_list  # 返回当前数据库内所有的表

    def create_table(self, table_name: str, field_dict: dict, native_sql: str = None) -> bool:
        """
        创建表，已存在直接返回，不存在则创建
        :param table_name: 表名
        :param field_dict: 表字段列表
        :return: 连接成功：返回 True
        """
        if native_sql is not None:
            self.sql = native_sql
        else:
            self.table_name = table_name.strip(" `'\"")  # 将表名赋值给实例属性

            self.field_list = field_dict.keys()  # 获取该表的所有的字段名

            table_list = self.show_table()  # 获取数据库里所有的表
            if self.table_name in table_list:  # 判断该表是否已存在
                return True  # 该表已存在！直接返回

            field_list = ["`{key}` {value}".format(key=key.strip(" `'\""), value=value) for key, value in field_dict.items()]
            create_field = ",".join(field_list)  # 将所有的字段与字段类型以 " , " 拼接
            self.sql = f"""CREATE TABLE `{self.table_name}`(
  {create_field}
);"""
        self.cursor.execute(self.sql)
        self.connect.commit()
        return True

    def _clone(self):
        """创建当前对象的副本"""
        clone = SQLite(connect=self.connect)
        clone.table_name = self.table_name
        clone.field_list = self.field_list.copy()
        clone.where_sql = self.where_sql.copy()
        clone.limit_sql = self.limit_sql
        clone.group_sql = self.group_sql
        clone.order_sql = self.order_sql
        clone.sql = self.sql
        clone.args = self.args.copy()
        return clone

    def table(self, table_name: str):
        """
        设置操作表
        :param table_name: 表名
        :return: self
        """
        self.table_name = table_name.strip(" `'\"")  # 表名
        self.field_list = []  # 表字段
        self.where_sql = []  # 条件语句
        self.limit_sql = ""  # 分页
        self.group_sql = ""  # 分组
        self.order_sql = ""  # 排序
        self.sql = ""  # 执行 sql
        self.args = []  # 条件参数
        return self

    def create(self, **kwargs) -> int:
        """
        添加一条数据
        :param kwargs: 字段 = 值
        :return: 返回创建 id
        """
        field_sql = "`,`".join([field.strip(" `'\"") for field in kwargs.keys()])
        create_sql = ",".join(["?"] * len(kwargs))

        self.sql = f"INSERT INTO `{self.table_name}`  (`{field_sql}`) VALUES ({create_sql});"
        args = list(kwargs.values())
        self.cursor.execute(self.sql, args)
        return self.cursor.lastrowid

    def fields(self, *fields):
        """
        查询字段
        :param fields: 字段
        :return: self
        """
        clone = self._clone()
        clone.field_list = fields
        return clone

    def where(self, sql: str, *args):
        """
        条件函数
        :param sql: sql 条件语句
        :param args: 值
        :return: self
        """
        clone = self._clone()
        clone.where_sql.append(sql)
        clone.args.extend(args)
        return clone

    def group_by(self, *orders, sql: str = ""):
        """
        分组函数
        :param orders: 分组字段
        :param sql: 分组sql语句
        :return: self
        """
        clone = self._clone()
        if sql:
            clone.group_sql = " " + sql
            return clone

        if len(orders) > 0:
            clone.group_sql = f" GROUP BY {', '.join(orders)}"
        else:
            clone.group_sql = ""
        return clone

    def order_by(self, *orders):
        """
        排序函数
        :param orders: 排序字段
        :return: self
        """
        clone = self._clone()
        order_fields = []
        for order in orders:
            order = str(order).strip(" `'\"")
            if not order:
                continue

            if order[0] == "-":
                order_sql = order[1:]
                sequence = "DESC"
            else:
                order_sql = order
                sequence = "ASC"
            order_fields.append(f"`{order_sql}` {sequence}")
        if len(order_fields) > 0:
            clone.order_sql = f" ORDER BY {', '.join(order_fields)}"
        else:
            clone.order_sql = ""
        return clone

    # 设置分页数据，返回总数据量，总页数
    def page(self, page: int, pagesize: int) -> Tuple[int, int]:
        """
        设置分页数据，返回总数据量，总页数
        :param page: 页码
        :param pagesize: 每页数量
        :return: (总数据量, 总页数)
        """
        if not isinstance(page, int):
            page = int(page)
        if not isinstance(pagesize, int):
            pagesize = int(pagesize)

        self.limit_sql = " LIMIT {size} OFFSET {offset}".format(
            size=pagesize,
            offset=(page - 1) * pagesize,
        )
        total = self.count()
        return total, math.ceil(total / pagesize)

    def select(self) -> List[dict]:
        """
        查询数据库，返回全部数据
        :return list[dict] 返回查询到的所有行
        """
        if len(self.field_list) == 0:
            self.field_list = self.__get_fields()

        fields_str = ", ".join(self.field_list)
        self.sql = f"SELECT {fields_str} FROM `{self.table_name}`"
        if len(self.where_sql) > 0:
            self.sql += f" WHERE {' AND '.join(self.where_sql)}"
        if self.group_sql:
            self.sql += self.group_sql
        if self.order_sql:
            self.sql += self.order_sql
        if self.limit_sql:
            self.sql += self.limit_sql

        self.cursor.execute(self.sql, self.args)
        rows = self.cursor.fetchall()
        result_field = self.__extract_field_list()
        return [dict(zip(result_field, row)) for row in rows]

    def find(self) -> Union[dict, None]:
        """
        查询数据库，返回第一条数据
        :return dict
        """
        if len(self.field_list) == 0:
            self.field_list = self.__get_fields()

        fields_str = ", ".join(self.field_list)
        self.sql = f"SELECT {fields_str} FROM `{self.table_name}`"
        if len(self.where_sql) > 0:
            self.sql += f" WHERE {' AND '.join(self.where_sql)}"
        if self.group_sql:
            self.sql += self.group_sql
        if self.order_sql:
            self.sql += self.order_sql

        self.sql += " LIMIT 1"
        self.cursor.execute(self.sql, self.args)
        row = self.cursor.fetchone()
        if row:
            result_field = self.__extract_field_list()
            kwargs = dict(zip(result_field, row))
            return kwargs
        return None

    def count(self) -> int:
        """
        查询条数
        :return 返回查询条数
        """
        self.sql = f"SELECT COUNT(*) FROM `{self.table_name}`"
        if len(self.where_sql) > 0:
            self.sql += f" WHERE {' AND '.join(self.where_sql)}"
        self.cursor.execute(self.sql, self.args)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return 0

    def exists(self) -> bool:
        """
        判断是否存在
        :return 返回 bool 类型
        """
        self.sql = f"SELECT 1 FROM `{self.table_name}`"
        if len(self.where_sql) > 0:
            self.sql += f" WHERE {' AND '.join(self.where_sql)}"

        self.cursor.execute(self.sql, self.args)
        return self.cursor.fetchone() is not None

    def update(self, **kwargs) -> int:
        """
        修改数据
        :param kwargs: key = value/字段 = 值 条件
        :return: 返回受影响的行
        """
        if not kwargs:
            raise ValueError("No fields to update")

        update_sql = ", ".join([f"`{field}`=?" for field in kwargs.keys()])
        self.sql = f"UPDATE `{self.table_name}` SET {update_sql}"
        if len(self.where_sql) > 0:
            self.sql += f" WHERE {' AND '.join(self.where_sql)}"

        args = list(kwargs.values())
        args.extend(self.args)

        self.cursor.execute(self.sql, args)
        return self.cursor.rowcount

    def delete(self) -> int:
        """
        删除满足条件的数据
        :return: 返回受影响的行
        """
        self.sql = f"DELETE FROM `{self.table_name}`"
        if len(self.where_sql) > 0:
            self.sql += f" WHERE {' AND '.join(self.where_sql)}"
        self.cursor.execute(self.sql, self.args)
        return self.cursor.rowcount

    def __get_fields(self) -> list:
        if self.table_name is None:
            return []

        self.sql = f"PRAGMA table_info(`{self.table_name}`);"
        self.cursor.execute(self.sql)
        field_list = [field[1] for field in self.cursor.fetchall()]
        return field_list

    def __extract_field_list(self) -> list:
        """
        解析字段列表，获取字段名称
        :return list 返回字段列表
        """
        result_field = []
        for field in self.field_list:
            if field == "*":
                result_field.extend(self.__get_fields())
            elif str(field).lower().find(" as ") != -1:
                field = field.split(" as ")[-1]

            field = field.strip(" `'\"")
            if not field:
                continue
            result_field.append(field)
        return result_field
