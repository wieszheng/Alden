#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2024/7/2 22:49
@Author   : wiesZheng
@Software : PyCharm
"""
import asyncio
import functools

from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any, Optional, Callable, AsyncIterator, Type, Union, TypeVar, List

from pydantic import BaseModel
from sqlalchemy import ColumnElement, or_, Select, asc, desc
from sqlalchemy.orm.util import AliasedClass

from loguru import logger
from sqlalchemy import Result, column, delete, func, select, text, update, URL
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.commons import SingletonMetaCls
from app.models import BaseOrmTable, async_session_maker

T_BaseOrmTable = TypeVar("T_BaseOrmTable", bound=BaseOrmTable)

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
UpdateSchemaInternalType = TypeVar("UpdateSchemaInternalType", bound=BaseModel)
DeleteSchemaType = TypeVar("DeleteSchemaType", bound=BaseModel)


def with_session(method):
    """
    兼容事务
    Args:
        method: orm 的 crud

    Notes:
        方法中没有带事务连接则，则构造

    Returns:
    """

    @functools.wraps(method)
    async def wrapper(db_manager, *args, **kwargs):
        try:
            session = kwargs.get("session") or None
            if session:
                return await method(db_manager, *args, **kwargs)
            else:
                async with async_session_maker() as session:
                    async with session.begin():
                        kwargs["session"] = session
                        return await method(db_manager, *args, **kwargs)
        except Exception as e:
            import traceback
            logger.exception(traceback.format_exc())
            logger.error(
                f"操作 {db_manager.orm_table.__name__} 失败\n"
                f"args：{[*args]}, kwargs：{kwargs}\n"
                f"方法：{method.__name__}\n"
                f"{e}\n"
            )

    return wrapper


def _extract_matching_columns_from_schema(
        model: Union[ModelType, AliasedClass],
        schema: Optional[type[BaseModel]],
        prefix: Optional[str] = None,
        alias: Optional[AliasedClass] = None,
        use_temporary_prefix: Optional[bool] = False,
        temp_prefix: Optional[str] = "joined__",
) -> list[Any]:
    """
    Retrieves a list of ORM column objects from a SQLAlchemy model that match the field names in a given Pydantic schema,
    or all columns from the model if no schema is provided. When an alias is provided, columns are referenced through
    this alias, and a prefix can be applied to column names if specified.

    Args:
        model: The SQLAlchemy ORM model containing columns to be matched with the schema fields.
        schema: Optional; a Pydantic schema containing field names to be matched with the model's columns. If `None`, all columns from the model are used.
        prefix: Optional; a prefix to be added to all column names. If `None`, no prefix is added.
        alias: Optional; an alias for the model, used for referencing the columns through this alias in the query. If `None`, the original model is used.
        use_temporary_prefix: Whether to use or not an aditional prefix for joins. Default `False`.
        temp_prefix: The temporary prefix to be used. Default `"joined__"`.

    Returns:
        A list of ORM column objects (potentially labeled with a prefix) that correspond to the field names defined
        in the schema or all columns from the model if no schema is specified. These columns are correctly referenced
        through the provided alias if one is given.
    """
    if not hasattr(model, "__table__"):
        raise AttributeError(f"{model.__name__} does not have a '__table__' attribute.")

    model_or_alias = alias if alias else model
    columns = []
    temp_prefix = (
        temp_prefix if use_temporary_prefix and temp_prefix is not None else ""
    )
    if schema:
        for field in schema.model_fields.keys():
            if hasattr(model_or_alias, field):
                column = getattr(model_or_alias, field)
                if prefix is not None or use_temporary_prefix:
                    column_label = (
                        f"{temp_prefix}{prefix}{field}"
                        if prefix
                        else f"{temp_prefix}{field}"
                    )
                    column = column.label(column_label)
                columns.append(column)
    else:
        for column in model.__table__.c:
            column = getattr(model_or_alias, column.key)
            if prefix is not None or use_temporary_prefix:
                column_label = (
                    f"{temp_prefix}{prefix}{column.key}"
                    if prefix
                    else f"{temp_prefix}{column.key}"
                )
                column = column.label(column_label)
            columns.append(column)

    return columns


class BaseManager(metaclass=SingletonMetaCls):
    orm_table: Type[ModelType] = None

    # def __init__(self,
    #              model: Type[ModelType],
    #              is_deleted_column: str = "is_deleted",
    #              deleted_at_column: str = "deleted_at"):
    #     self.model = model
    #     self.is_deleted_column = is_deleted_column
    #     self.deleted_at_column = deleted_at_column

    _SUPPORTED_FILTERS = {
        "gt": lambda column: column.__gt__,
        "lt": lambda column: column.__lt__,
        "gte": lambda column: column.__ge__,
        "lte": lambda column: column.__le__,
        "ne": lambda column: column.__ne__,
        "is": lambda column: column.is_,
        "is_not": lambda column: column.is_not,
        "like": lambda column: column.like,
        "notlike": lambda column: column.notlike,
        "ilike": lambda column: column.ilike,
        "notilike": lambda column: column.notilike,
        "startswith": lambda column: column.startswith,
        "endswith": lambda column: column.endswith,
        "contains": lambda column: column.contains,
        "match": lambda column: column.match,
        "between": lambda column: column.between,
        "in": lambda column: column.in_,
        "not_in": lambda column: column.not_in,
    }

    def _get_sqlalchemy_filter(
            self,
            operator: str,
            value: Any,
    ) -> Optional[Callable[[str], Callable]]:
        if operator in {"in", "not_in", "between"}:
            if not isinstance(value, (tuple, list, set)):
                raise ValueError(f"<{operator}> filter must be tuple, list or set")
        return self._SUPPORTED_FILTERS.get(operator)

    def _parse_filters(
            self, model: Optional[Union[type[ModelType], AliasedClass]] = None, **kwargs
    ) -> list[ColumnElement]:
        model = model or self.orm_table
        filters = []

        for key, value in kwargs.items():
            if "__" in key:
                field_name, op = key.rsplit("__", 1)
                column = getattr(model, field_name, None)
                if column is None:
                    raise ValueError(f"Invalid filter column: {field_name}")
                if op == "or":
                    or_filters = [
                        sqlalchemy_filter(column)(or_value)
                        for or_key, or_value in value.items()
                        if (
                               sqlalchemy_filter := self._get_sqlalchemy_filter(
                                   or_key, value
                               )
                           )
                           is not None
                    ]
                    filters.append(or_(*or_filters))
                else:
                    sqlalchemy_filter = self._get_sqlalchemy_filter(op, value)
                    if sqlalchemy_filter:
                        filters.append(sqlalchemy_filter(column)(value))
            else:
                column = getattr(model, key, None)
                if column is not None:
                    filters.append(column == value)

        return filters

    def _apply_sorting(
            self,
            stmt: Select,
            sort_columns: Union[str, list[str]],
            sort_orders: Optional[Union[str, list[str]]] = None,
    ) -> Select:
        """
        Apply sorting to a SQLAlchemy query based on specified column names and sort orders.

        Args:
            stmt: The SQLAlchemy `Select` statement to which sorting will be applied.
            sort_columns: A single column name or a list of column names on which to apply sorting.
            sort_orders: A single sort order (`"asc"` or `"desc"`) or a list of sort orders corresponding
                to the columns in `sort_columns`. If not provided, defaults to `"asc"` for each column.

        Raises:
            ValueError: Raised if sort orders are provided without corresponding sort columns,
                or if an invalid sort order is provided (not `"asc"` or `"desc"`).
            ArgumentError: Raised if an invalid column name is provided that does not exist in the model.

        Returns:
            The modified `Select` statement with sorting applied.

        Examples:
            Applying ascending sort on a single column:
            >>> stmt = _apply_sorting(stmt, 'name')

            Applying descending sort on a single column:
            >>> stmt = _apply_sorting(stmt, 'age', 'desc')

            Applying mixed sort orders on multiple columns:
            >>> stmt = _apply_sorting(stmt, ['name', 'age'], ['asc', 'desc'])

            Applying ascending sort on multiple columns:
            >>> stmt = _apply_sorting(stmt, ['name', 'age'])

        Note:
            This method modifies the passed `Select` statement in-place by applying the `order_by` clause
            based on the provided column names and sort orders.
        """
        if sort_orders and not sort_columns:
            raise ValueError("Sort orders provided without corresponding sort columns.")

        if sort_columns:
            if not isinstance(sort_columns, list):
                sort_columns = [sort_columns]

            if sort_orders:
                if not isinstance(sort_orders, list):
                    sort_orders = [sort_orders] * len(sort_columns)
                if len(sort_columns) != len(sort_orders):
                    raise ValueError(
                        "The length of sort_columns and sort_orders must match."
                    )

                for idx, order in enumerate(sort_orders):
                    if order not in ["asc", "desc"]:
                        raise ValueError(
                            f"Invalid sort order: {order}. Only 'asc' or 'desc' are allowed."
                        )

            validated_sort_orders = (
                ["asc"] * len(sort_columns) if not sort_orders else sort_orders
            )

            for idx, column_name in enumerate(sort_columns):
                column = getattr(self.orm_table, column_name, None)
                if not column:
                    raise ValueError(f"Invalid column name: {column_name}")

                order = validated_sort_orders[idx]
                stmt = stmt.order_by(asc(column) if order == "asc" else desc(column))

        return stmt

    @with_session
    async def create(
            self,
            *,
            object: CreateSchemaType,
            commit: bool = True,
            session: AsyncSession = None,
    ) -> ModelType:
        """
        Create a new record in the database.

        Args:
            object: The Pydantic schema containing the data to be saved.
            commit: If `True`, commits the transaction immediately. Default is `True`.
            session: The SQLAlchemy async session.

        Returns:
            The created database object.
        """
        object_dict = object.model_dump()
        db_object: ModelType = self.orm_table(**object_dict)
        session.add(db_object)
        if commit:
            await session.commit()
        return db_object

    async def select(
            self,
            schema_to_select: Optional[type[BaseModel]] = None,
            sort_columns: Optional[Union[str, list[str]]] = None,
            sort_orders: Optional[Union[str, list[str]]] = None,
            **kwargs,
    ) -> Select:
        """
        Constructs a SQL Alchemy `Select` statement with optional column selection, filtering, and sorting.

        This method allows for advanced filtering through comparison operators, enabling queries to be refined beyond simple equality checks.

        For filtering details see [the Advanced Filters documentation](../../advanced/crud/#advanced-filters)

        Args:
            schema_to_select: Pydantic schema to determine which columns to include in the selection. If not provided, selects all columns of the model.
            sort_columns: A single column name or list of column names to sort the query results by. Must be used in conjunction with `sort_orders`.
            sort_orders: A single sort order (`"asc"` or `"desc"`) or a list of sort orders, corresponding to each column in `sort_columns`. If not specified, defaults to ascending order for all `sort_columns`.
            **kwargs: Filters to apply to the query, including advanced comparison operators for more detailed querying.

        Returns:
            An SQL Alchemy `Select` statement object that can be executed or further modified.

        Examples:
            Selecting specific columns with filtering and sorting:
            ```python
            stmt = await crud.select(
                schema_to_select=UserReadSchema,
                sort_columns=['age', 'name'],
                sort_orders=['asc', 'desc'],
                age__gt=18,
            )
            ```

            Creating a statement to select all users without any filters:
            ```python
            stmt = await crud.select()
            ```

            Selecting users with a specific `role`, ordered by `name`:
            ```python
            stmt = await crud.select(
                schema_to_select=UserReadSchema,
                sort_columns='name',
                role='admin',
            )
            ```
        Note:
            This method does not execute the generated SQL statement.
            Use `db.execute(stmt)` to run the query and fetch results.
        """
        to_select = _extract_matching_columns_from_schema(
            model=self.orm_table, schema=schema_to_select
        )
        filters = self._parse_filters(**kwargs)
        stmt = select(*to_select).filter(*filters)

        if sort_columns:
            stmt = self._apply_sorting(stmt, sort_columns, sort_orders)
        return stmt

    @with_session
    async def bulk_delete_by_ids(
            self,
            pk_ids: list,
            *,
            orm_table: Type[BaseOrmTable] = None,
            logic_del: bool = False,
            logic_field: str = "deleted_at",
            logic_del_set_value: Any = None,
            session: AsyncSession = None,
    ):
        """
        根据主键id批量删除
        Args:
            pk_ids: 主键id列表
            orm_table: orm表映射类
            logic_del: 逻辑删除，默认 False 物理删除 True 逻辑删除
            logic_field: 逻辑删除字段 默认 deleted_at
            logic_del_set_value: 逻辑删除字段设置的值
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns: 删除的记录数
        """
        orm_table = orm_table or self.orm_table
        conds = [orm_table.id.in_(pk_ids)]
        return await self.delete(
            conds=conds,
            orm_table=orm_table,
            logic_del=logic_del,
            logic_field=logic_field,
            logic_del_set_value=logic_del_set_value,
            session=session,
        )

    @with_session
    async def delete_by_id(
            self,
            pk_id: int,
            *,
            orm_table: Type[BaseOrmTable] = None,
            logic_del: bool = False,
            logic_field: str = "deleted_at",
            logic_del_set_value: Any = None,
            session: AsyncSession = None,
    ):
        """
        根据主键id删除
        Args:
            pk_id: 主键id
            orm_table: orm表映射类
            logic_del: 逻辑删除，默认 False 物理删除 True 逻辑删除
            logic_field: 逻辑删除字段 默认 deleted_at
            logic_del_set_value: 逻辑删除字段设置的值
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns: 删除的记录数
        """
        orm_table = orm_table or self.orm_table
        conds = [orm_table.id == pk_id]
        return await self.delete(
            conds=conds,
            orm_table=orm_table,
            logic_del=logic_del,
            logic_field=logic_field,
            logic_del_set_value=logic_del_set_value,
            session=session,
        )

    @with_session
    async def delete(
            self,
            *,
            conds: list = None,
            orm_table: Type[BaseOrmTable] = None,
            logic_del: bool = False,
            logic_field: str = "deleted_at",
            logic_del_set_value: Any = None,
            session: AsyncSession = None,
    ):
        """
        通用删除
        Args:
            conds: 条件列表, e.g. [UserTable.id == 1]
            orm_table: orm表映射类
            logic_del: 逻辑删除，默认 False 物理删除 True 逻辑删除
            logic_field: 逻辑删除字段 默认 deleted_at
            logic_del_set_value: 逻辑删除字段设置的值
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns: 删除的记录数
        """
        orm_table = orm_table or self.orm_table

        if logic_del:
            # 执行逻辑删除操作
            logic_del_info = dict()
            logic_del_info[logic_field] = logic_del_set_value or datetime.now()
            delete_stmt = update(orm_table).where(*conds).values(**logic_del_info)
        else:
            # 执行物理删除操作
            delete_stmt = delete(orm_table).where(*conds)

        cursor_result = await session.execute(delete_stmt)

        # 返回影响的记录数
        return cursor_result.rowcount

    @with_session
    async def bulk_add(
            self,
            table_objs: List[Union[T_BaseOrmTable, dict]],
            *,
            orm_table: Type[BaseOrmTable] = None,
            flush: bool = False,
            session: AsyncSession = None,
    ) -> List[T_BaseOrmTable]:
        """
        批量插入
        Args:
            table_objs: orm映射类实例列表
                e.g. [UserTable(username="hui", age=18), ...] or [{"username": "hui", "age": 18}, ...]
            orm_table: orm表映射类
            flush: 刷新对象状态，默认不刷新
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns:
            成功插入的对象列表
        """
        orm_table = orm_table or self.orm_table
        if all(isinstance(table_obj, dict) for table_obj in table_objs):
            # 字典列表转成orm映射类实例列表处理
            table_objs = [orm_table(**table_obj) for table_obj in table_objs]

        session.add_all(table_objs)
        if flush:
            await session.flush(table_objs)

        return table_objs

    @with_session
    async def add(
            self, table_obj: [T_BaseOrmTable, dict], *, orm_table: Type[BaseOrmTable] = None,
            session: AsyncSession = None
    ) -> int:
        """
        插入一条数据
        Args:
            table_obj: orm映射类实例对象, eg. UserTable(username="hui", age=18) or {"username": "hui", "age": 18}
            orm_table: orm表映射类
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns: 新增的id
            table_obj.id
        """
        orm_table = orm_table or self.orm_table
        if isinstance(table_obj, dict):
            table_obj = orm_table(**table_obj)

        session.add(table_obj)
        await session.flush(objects=[table_obj])  # 刷新对象状态，获取新增的id
        return table_obj.id

    @with_session
    async def query_by_id(
            self,
            pk_id: int,
            *,
            orm_table: Type[BaseOrmTable] = None,
            session: AsyncSession = None,
    ) -> Union[T_BaseOrmTable, None]:
        """
        根据主键id查询
        Args:
            pk_id: 主键id
            orm_table: orm表映射类
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns:
            orm映射类的实例对象
        """
        orm_table = orm_table or self.orm_table
        ret = await session.get(orm_table, pk_id)
        return ret

    @with_session
    async def _query(
            self,
            *,
            cols: list = None,
            orm_table: BaseOrmTable = None,
            conds: list = None,
            orders: list = None,
            limit: int = None,
            offset: int = 0,
            session: AsyncSession = None,
    ) -> Result[Any]:
        """
        通用查询
        Args:
            cols: 查询的列表字段
            orm_table: orm表映射类
            conds: 查询的条件列表
            orders: 排序列表, 默认id升序
            limit: 限制数量大小
            offset: 偏移量
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns: 查询结果集
            cursor_result
        """
        cols = cols or []
        cols = [column(col_obj) if isinstance(col_obj, str) else col_obj for col_obj in cols]  # 兼容字符串列表

        conditions = conds or []
        orders = orders or [column("id")]
        orm_table = orm_table or self.orm_table

        # 构造查询
        if cols:
            # 查询指定列
            query_sql = select(*cols).select_from(orm_table).where(*conditions).order_by(*orders)
        else:
            # 查询全部字段
            query_sql = select(orm_table).where(*conditions).order_by(*orders)

        if limit:
            query_sql = query_sql.limit(limit).offset(offset)

        # 执行查询
        cursor_result = await session.execute(query_sql)
        return cursor_result

    @with_session
    async def query_one(
            self,
            *,
            cols: list = None,
            orm_table: Type[BaseOrmTable] = None,
            conds: list = None,
            orders: list = None,
            flat: bool = False,
            session: AsyncSession = None,
    ) -> Union[dict, T_BaseOrmTable, Any]:
        """
        查询单行
        Args:
            cols: 查询的列表字段
            orm_table: orm表映射类
            conds: 查询的条件列表
            orders: 排序列表
            flat: 单字段时扁平化处理
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Examples:
            # 指定列名
            ret = await UserManager().query_one(cols=["username", "age"], conds=[UserTable.id == 1])
            sql => select username, age from user where id=1
            ret => {"username": "hui", "age": 18}

            # 指定列名，单字段扁平化处理
            ret = await UserManager().query_one(cols=["username"], conds=[UserTable.id == 1])
            sql => select username from user where id=1
            ret => {"username": "hui"} => "hui"

            # 计算总数
            ret = await UserManager().query_one(cols=[func.count()])
            sql => select count(*) as count from user
            ret => {"count": 10} => 10

            # 不指定列名，查询全部字段, 返回表实例对象
            ret = await UserManager().query_one(conds=[UserTable.id == 1])
            sql => select id, username, age from user where id=1
            ret => UserTable(id=1, username="hui", age=18)

        Returns:
            Union[dict, BaseOrmTable(), Any(flat=True)]
        """
        cursor_result = await self._query(cols=cols, orm_table=orm_table, conds=conds, orders=orders, session=session)
        if cols:
            if flat and len(cols) == 1:
                # 单行单字段查询: 直接返回字段结果
                # eg: select count(*) as count from user 从 {"count": 100} => 100
                # eg: select username from user where id=1 从 {"username": "hui"} => "hui"
                return cursor_result.scalar_one()

            # eg: select username, age from user where id=1 => {"username": "hui", "age": 18}
            return cursor_result.mappings().one() or {}
        else:
            # 未指定列名查询默认全部字段，返回的是表实例对象 BaseOrmTable()
            # eg: select id, username, age from user where id=1 => UserTable(id=1, username="hui", age=18)
            return cursor_result.scalar_one()

    @with_session
    async def query_all(
            self,
            *,
            cols: list = None,
            orm_table: BaseOrmTable = None,
            conds: list = None,
            orders: list = None,
            flat: bool = False,
            limit: int = None,
            offset: int = None,
            session: AsyncSession = None,
    ) -> Union[List[dict], List[T_BaseOrmTable], Any]:
        """
        查询多行
        Args:
            cols: 查询的列表字段
            orm_table: orm表映射类
            conds: 查询的条件列表
            orders: 排序列表
            flat: 单字段时扁平化处理
            limit: 限制数量大小
            offset: 偏移量
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务
        """
        cursor_result = await self._query(
            cols=cols, orm_table=orm_table, conds=conds, orders=orders, limit=limit, offset=offset, session=session
        )
        if cols:
            if flat and len(cols) == 1:
                # 扁平化处理
                # eg: select id from user 从 [{"id": 1}, {"id": 2}, {"id": 3}] => [1, 2, 3]
                return cursor_result.scalars().all()

            # eg: select username, age from user => [{"username": "hui", "age": 18}, [{"username": "dbk", "age": 18}]]
            return cursor_result.mappings().all() or []
        else:
            # 未指定列名查询默认全部字段，返回的是表实例对象 [BaseOrmTable()]
            # eg: select id, username, age from user
            # [User(id=1, username="hui", age=18), User(id=2, username="dbk", age=18)
            return cursor_result.scalars().all()

    async def list_page(
            self,
            cols: list = None,
            orm_table: BaseOrmTable = None,
            conds: list = None,
            orders: list = None,
            curr_page: int = 1,
            page_size: int = 20,
            session: AsyncSession = None,
    ):
        """
        单表通用分页查询
        Args:
            cols: 查询的列表字段
            orm_table: orm表映射类
            conds: 查询的条件列表
            orders: 排序列表
            curr_page: 页码
            page_size: 每页数量
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns: total_count, data_list
        """
        conds = conds or []
        orders = orders or [column("id")]
        orm_table = orm_table or self.orm_table

        limit = page_size
        offset = (curr_page - 1) * page_size
        total_count, data_list = await asyncio.gather(
            self.query_one(cols=[func.count()], orm_table=orm_table, conds=conds, orders=orders, flat=True,
                           session=session),
            self.query_all(
                cols=cols, orm_table=orm_table, conds=conds, orders=orders, limit=limit, offset=offset, session=session
            ),
        )

        return total_count, data_list

    @with_session
    async def update(
            self,
            values: dict,
            orm_table: Type[BaseOrmTable] = None,
            conds: list = None,
            session: AsyncSession = None,
    ):
        """
        更新数据
        Args:
            values: 要更新的字段和对应的值，字典格式，例如 {"field1": value1, "field2": value2, ...}
            orm_table: ORM表映射类
            conds: 更新条件列表，每个条件为一个表达式，例如 [UserTable.username == "hui", ...]
            session: 数据库会话对象，如果为 None，则在方法内部开启新的事务

        Returns: 影响的行数
            cursor_result.rowcount
        """
        orm_table = orm_table or self.orm_table
        conds = conds or []
        values = values or {}
        if not values:
            return
        sql = update(orm_table).where(*conds).values(**values)
        cursor_result = await session.execute(sql)
        return cursor_result.rowcount

    @with_session
    async def update_or_add(
            self,
            table_obj: [T_BaseOrmTable, dict],
            *,
            orm_table: Type[BaseOrmTable] = None,
            session: AsyncSession = None,
            **kwargs,
    ):
        """
        指定对象更新or添加数据
        Args:
            table_obj: 映射类实例对象 or dict，
                e.g. UserTable(username="hui", age=18) or {"username": "hui", "v": 18, ...}
            orm_table: ORM表映射类
            session: 数据库会话对象，如果为 None，则在方法内部开启新的事务

        Returns:
        """
        orm_table = orm_table or self.orm_table
        if isinstance(table_obj, dict):
            table_obj = orm_table(**table_obj)

        return await session.merge(table_obj, **kwargs)

    @with_session
    async def run_sql(
            self, sql: str, *, params: dict = None, query_one: bool = False, session: AsyncSession = None
    ) -> Union[dict, List[dict]]:
        """
        执行并提交单条sql
        Args:
            sql: sql语句
            params: sql参数, eg. {":id_val": 10, ":name_val": "hui"}
            query_one: 是否查询单条，默认False查询多条
            session: 数据库会话对象，如果为 None，则通过装饰器在方法内部开启新的事务

        Returns:
            执行sql的结果
        """
        sql = text(sql)
        cursor_result = await session.execute(sql, params)
        if query_one:
            return cursor_result.mappings().one() or {}
        else:
            return cursor_result.mappings().all() or []
