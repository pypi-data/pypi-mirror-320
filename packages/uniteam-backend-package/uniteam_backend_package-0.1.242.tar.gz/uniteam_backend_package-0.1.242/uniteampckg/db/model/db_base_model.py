"""
This Module contains the BaseTableModel class which is used to define the base class for defining table models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import (
    Optional,
    List,
    Any,
    get_origin,
    get_args,
    Union,
    TypeVar,
    Type,
    ClassVar,
)
import datetime
import uuid
from uniteampckg.db.db_util import DbUtil
from uniteampckg.utils.decorators.common_decorator import handle_function_exception
from uniteampckg.utils.logging.logger import Logger
from uniteampckg.models.base_models import FunctionResp
import json

logger = Logger("BaseTableModel")
logger.configure_logging()

T = TypeVar("T", bound="BaseTableModel")


class ColumnMetadata(BaseModel):
    """
    Used to define metadata for a column.
    Used in the metadata field of a Field object.
    """

    db_default: Optional[Any] = None
    index: Optional[bool] = False
    nullable: Optional[bool] = False
    primary_key: Optional[bool] = False
    unique: Optional[bool] = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    is_timezone_aware: Optional[bool] = False


def Column(
    default: Optional[Any] = None,
    db_default: Optional[Any] = None,
    index: Optional[bool] = False,
    nullable: Optional[bool] = False,
    primary_key: Optional[bool] = False,
    unique: Optional[bool] = False,
    foreign_key_table: Optional[str] = None,
    foreign_key_column: Optional[str] = None,
    is_timezone_aware: Optional[bool] = False,
) -> Any:
    f = Field(default=default)

    f.metadata.append(
        ColumnMetadata(
            db_default=db_default,
            index=index,
            nullable=nullable,
            primary_key=primary_key,
            unique=unique,
            foreign_key_table=foreign_key_table,
            foreign_key_column=foreign_key_column,
            is_timezone_aware=is_timezone_aware,
        ).model_dump(exclude_unset=True)
    )

    return f


class BaseTableModel(BaseModel, extra="allow"):
    """
    Base class for defining table models. Includes utility methods for schema and data.
    """

    model_config = ConfigDict(ser_json_timedelta="iso8601")

    # STATIC METHODS
    @staticmethod
    def format_value(value: Any) -> str:
        """
        Format the value for SQL insertion.
        """
        if isinstance(value, str):
            return f"{value}"
        elif isinstance(value, list):
            return f"ARRAY[{', '.join([f'\"{v}\"' for v in value])}]"
        elif isinstance(value, datetime.timedelta):
            days = value.days
            seconds = value.seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days} days {hours:02}:{minutes:02}:{seconds:02}"
        elif isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, bool):
            return value

        return str(value)

    @staticmethod
    def classname_to_table_name(classname: str) -> str:
        """
        Convert a class name to a table name.
        lower the name, then convert from PascalCase to snake_case.
        """
        table_name = classname[0].lower()
        for char in classname[1:]:
            if char.isupper():
                table_name += "_"
            table_name += char.lower()
        return table_name

    @staticmethod
    def get_db_type(python_type: Any, metadata: Optional[ColumnMetadata] = None) -> str:
        """
        Maps Python types to PostgreSQL data types.
        """
        type_mapping = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
            datetime.datetime: (
                "TIMESTAMPZ"
                if metadata is not None and metadata.is_timezone_aware is True
                else "TIMESTAMP"
            ),
            datetime.date: "DATE",
            datetime.time: "TIME",
            datetime.timedelta: "INTERVAL",
            bool: "BOOLEAN",
            dict: "JSONB",
        }

        origin = get_origin(python_type)
        if origin is Union:
            args = get_args(python_type)
            if type(None) in args:
                non_none_type = next(arg for arg in args if arg is not type(None))
                return BaseTableModel.get_db_type(non_none_type, metadata)
        elif origin is list:
            item_type = get_args(python_type)[0]
            item_db_type = type_mapping.get(item_type, "TEXT")
            return f"{item_db_type}[]"

        return type_mapping.get(python_type, "TEXT")

    # INSTANCE METHODS -------------------------------------------------------
    @classmethod
    def get_table_name(cls) -> str:
        """
        Get the table name for the model.
        """
        return cls.classname_to_table_name(cls.__name__)

    @classmethod
    def get_columns(cls) -> List[str]:
        """
        Get a list of column names.
        """
        return list(cls.__annotations__.keys())

    @classmethod
    def get_primary_keys(cls) -> List[str]:
        """
        Get a list of primary key column names.
        """
        primary_keys = []
        for name, field in cls.__annotations__.items():
            if (
                hasattr(cls.model_fields[name], "metadata")
                and len(cls.model_fields[name].metadata) > 0
            ):
                metadata = ColumnMetadata(**cls.model_fields[name].metadata[0])
                if metadata.primary_key:
                    primary_keys.append(name)
        return primary_keys

    @classmethod
    def get_foreign_keys(cls) -> List[str]:
        """
        Get a list of foreign key column names.
        return a list of dictionaries with the following
        keys: column, ref_table, ref_column
        """
        foreign_keys = []
        for name, field in cls.__annotations__.items():
            if (
                hasattr(cls.model_fields[name], "metadata")
                and len(cls.model_fields[name].metadata) > 0
            ):
                metadata = ColumnMetadata(**cls.model_fields[name].metadata[0])
                if metadata.foreign_key_table is not None:
                    foreign_keys.append(
                        {
                            "column": name,
                            "ref_table": metadata.foreign_key_table,
                            "ref_column": metadata.foreign_key_column,
                        }
                    )
        return foreign_keys

    # DDL METHODS -----------------------------------------------------------
    @classmethod
    def generate_ddl_query(cls, recreate: bool = False) -> str:
        """
        Generate the DDL query for creating the table based on the Pydantic fields.
        It'll also create indexes and foreign keys based on the json_schema_extra.
        """
        columns = []
        primary_keys = []
        foreign_keys = []
        indexes = []

        for name, field in cls.__annotations__.items():
            constraints = []

            metadata: ColumnMetadata = None
            if (
                hasattr(cls.model_fields[name], "metadata")
                and len(cls.model_fields[name].metadata) > 0
            ):
                metadata = ColumnMetadata(**cls.model_fields[name].metadata[0])

            db_type = cls.get_db_type(field, metadata)

            if metadata is not None:
                if metadata.primary_key:
                    primary_keys.append(name)
                    constraints.append("NOT NULL")

                if metadata.unique:
                    constraints.append("UNIQUE")

                if metadata.db_default is not None:
                    db_default = metadata.db_default
                    constraints.append(
                        f"DEFAULT '{db_default}'"
                        if isinstance(db_default, str)
                        else f"DEFAULT {db_default}"
                    )

                if metadata.nullable:
                    constraints.append("NULL")

                if metadata.foreign_key_table is not None:
                    foreign_keys.append(
                        f"FOREIGN KEY ({name}) REFERENCES {metadata.foreign_key_table} ({metadata.foreign_key_column})"
                    )

                if metadata.index:
                    indexes.append(f"CREATE INDEX ON {cls.get_table_name()} ({name});")

            columns.append(f"{name} {db_type} {' '.join(constraints)}")

        primary_key_str = (
            f", PRIMARY KEY ({', '.join(primary_keys)})" if primary_keys else ""
        )
        foreign_key_str = ", ".join(foreign_keys)
        query = f"CREATE TABLE {'IF NOT EXISTS ' if not recreate else ''}{cls.classname_to_table_name(cls.__name__)} ("
        query += ",".join(columns) + primary_key_str
        if foreign_keys:
            query += f", {foreign_key_str}"
        query += ");"

        for index in indexes:
            query += f"\n{index}"

        logger.info(f"DDL Query: {query}")

        return query

    # DQL METHODS -----------------------------------------------------------
    @classmethod
    def select_one(
        cls: Type[T],
        db_conn: DbUtil = None,
        select_columns: List[str] = None,
        and_condition_columns: List[str] = None,
        and_condition_value: List[Any] = None,
        custom_condition_query: str = None,
        custom_query_inputs: List[Any] = None,
        or_condition_columns: List[str] = None,
        or_condition_value: List[Any] = None,
        order_by_columns: List[str] = None,
        order_direction: str = "ASC",
    ) -> T:
        """
        Generate the DQL query for selecting one row from the table.
        """
        print("select_one")
        if db_conn is None:
            db_conn = DbUtil()
            if not db_conn.connect().status:
                raise Exception("Database connection failed")

        if select_columns is None:
            select_columns = ["*"]

        condition_str_grps: List[str] = []
        condition_value: List[Any] = []

        if custom_condition_query is not None:
            condition_str = custom_condition_query
            condition_value = custom_query_inputs
        else:
            if and_condition_columns is not None and and_condition_value is not None:
                condition_str_grps.append(
                    "("
                    + " AND ".join(
                        [f"{column} = %s" for column in and_condition_columns]
                    )
                    + ")"
                )
                condition_value += and_condition_value

            if or_condition_columns is not None and or_condition_value is not None:
                condition_str_grps.append(
                    "("
                    + " OR ".join([f"{column} = %s" for column in or_condition_columns])
                    + ")"
                )
                condition_value += or_condition_value

        query = f"SELECT {', '.join(select_columns)} FROM {cls.get_table_name()}"

        if len(condition_str_grps) > 0:
            condition_str = " AND ".join(condition_str_grps)
            query += f" WHERE {condition_str}"

        if order_by_columns is not None:
            query += f" ORDER BY {', '.join(order_by_columns)} {order_direction}"

        query += " LIMIT 1;"

        logger.info(f"Select One Query: {query}")
        logger.info(f"Select One Values: {condition_value}")

        result = db_conn.execute_query(
            query=query,
            data=tuple(condition_value),
            commit=False,
            get_column_names=True,
        )

        if not result.status:
            raise Exception("Select query failed")

        if len(result.data) > 0:
            data = dict(result.data[0])
            return cls(**data)

        return None

    @classmethod
    def select_many(
        cls: Type[T],
        db_conn: DbUtil = None,
        select_columns: List[str] = None,
        and_condition_columns: List[str] = None,
        and_condition_value: List[Any] = None,
        custom_condition_query: str = None,
        custom_query_inputs: List[Any] = None,
        or_condition_columns: List[str] = None,
        or_condition_value: List[Any] = None,
        order_by_columns: List[str] = None,
        order_direction: str = "ASC",
        group_by_columns: List[str] = None,
        limit: int = None,
        offset: int = None,
    ) -> List[T]:
        """
        Generate the DQL query for selecting multiple rows from the table.
        """

        if db_conn is None:
            db_conn = DbUtil()
            if not db_conn.connect().status:
                raise Exception("Database connection failed")

        if select_columns is None:
            select_columns = ["*"]

        condition_str_grps: List[str] = []
        condition_value: List[Any] = []

        if custom_condition_query is not None:
            condition_str = custom_condition_query
            condition_value = custom_query_inputs

        else:
            if and_condition_columns is not None and and_condition_value is not None:
                condition_str_grps.append(
                    "("
                    + " AND ".join(
                        [f"{column} = %s" for column in and_condition_columns]
                    )
                    + ")"
                )
                condition_value += and_condition_value

            if or_condition_columns is not None and or_condition_value is not None:
                condition_str_grps.append(
                    "("
                    + " OR ".join([f"{column} = %s" for column in or_condition_columns])
                    + ")"
                )
                condition_value += or_condition_value

        query = f"SELECT {', '.join(select_columns)} FROM {cls.get_table_name()}"

        if len(condition_str_grps) > 0:
            condition_str = " AND ".join(condition_str_grps)
            query += f" WHERE {condition_str}"

        if group_by_columns is not None:
            query += f" GROUP BY {', '.join(group_by_columns)}"

        if order_by_columns is not None:
            query += f" ORDER BY {', '.join(order_by_columns)} {order_direction}"

        if limit is not None:
            query += f" LIMIT {limit}"

        if offset is not None:
            query += f" OFFSET {offset}"

        query += ";"

        logger.info(f"Select Many Query: {query}")
        logger.info(f"Select Many Values: {condition_value}")

        result = db_conn.execute_query(
            query=query,
            data=tuple(condition_value),
            commit=False,
            get_column_names=True,
        )

        if not result.status:
            raise Exception("Select query failed")

        if len(result.data) > 0:
            data = [cls(**dict(row)) for row in result.data]
            return data

        return []
    
    @classmethod
    def delete(
        cls : Type[T],
        db_conn: DbUtil = None,
        self_commit: bool = True,
        condition_columns: List[str] = None,
        condition_value: List[Any] = None,
    ) -> FunctionResp:
        """
        Generate the DML query for deleting the row from the table.
        """
        if db_conn is None:
            db_conn = DbUtil()
            if not db_conn.connect().status:
                raise Exception("Database connection failed")

        if condition_columns is None or condition_value is None:
            raise Exception("Condition columns and values are required")

        condition_str = " AND ".join([f"{column} = %s" for column in condition_columns])

        query = f"DELETE FROM {cls.get_table_name()} WHERE {condition_str};"

        logger.info(f"Delete Query: {query}")
        logger.info(f"Delete Values: {condition_str}")

        db_conn.execute_query(
            query=query, data=tuple(condition_value), commit=self_commit
        )

        return FunctionResp(status=True)

    # DML METHODS -----------------------------------------------------------
    @handle_function_exception
    def insert(
        cls,
        db_conn: DbUtil = None,
        self_commit: bool = True,
        update_on_conflict: bool = False,
        do_not_execute: bool = False,
    ) -> FunctionResp[dict]:
        """
        Generate the DML query for inserting the row into the table.
        Params:
        - db_conn: Database connection object (optional)
        - self_commit: Commit the transaction (optional)
        - update_on_conflict: Update the row on conflict with primary keys (optional)
        - do_not_execute: Do not execute the query, just return the query and values (optional)
        Returns:
        - FunctionResp object with status and data (query and values)
        """
        columns = []
        values = []

        if db_conn is None:
            db_conn = DbUtil()
            if not db_conn.connect().status:
                raise Exception("Database connection failed")

        for name, field in cls.__annotations__.items():
            value = getattr(cls, name)
            if value is not None:
                columns.append(name)
                values.append(cls.format_value(value))

        ss = ", ".join(["%s" for _ in values])

        query = (
            f"INSERT INTO {cls.get_table_name()} ({', '.join(columns)}) VALUES ({ss})"
        )

        if update_on_conflict:
            # On conflict with primary keys, upadte the row
            query += " ON CONFLICT ("
            query += ", ".join(cls.get_primary_keys()) + ") DO UPDATE SET "
            query += ", ".join(
                [
                    f"{column} = EXCLUDED.{column}"
                    for column in columns
                    if column not in cls.get_primary_keys()
                ]
            )

        query += ";"

        logger.info(f"Insert Query: {query}")
        logger.info(f"Insert Values: {values}")

        if not do_not_execute:
            db_conn.execute_query(
                query=query, data=tuple(values), commit=self_commit, no_fetch=True
            )

        return FunctionResp[dict](status=True, data={"query": query, "values": values})

    @handle_function_exception
    def update(
        cls,
        db_conn: DbUtil = None,
        self_commit: bool = True,
        condition_columns: List[str] = None,
        condition_value: List[Any] = None,
    ) -> FunctionResp:
        """
        Generate the DML query for updating the row in the table.
        """
        columns = []
        values = []

        if db_conn is None:
            db_conn = DbUtil()
            if not db_conn.connect().status:
                raise Exception("Database connection failed")

        primary_keys = cls.get_primary_keys()

        for name, field in cls.__annotations__.items():
            value = getattr(cls, name)
            if value is not None and name not in primary_keys:
                columns.append(name)
                values.append(cls.format_value(value))

        ss = ", ".join([f"{column} = %s" for column in columns])

        condition_str = ""
        if condition_columns is None or condition_value is None:
            condition_str = " AND ".join([f"{column} = %s" for column in primary_keys])
            condition_value = [getattr(cls, column) for column in primary_keys]

        else:
            condition_str = " AND ".join(
                [f"{column} = %s" for column in condition_columns]
            )
            condition_value = condition_value

        query = f"UPDATE {cls.get_table_name()} SET {ss} WHERE {condition_str};"

        logger.info(f"Update Query: {query}")
        logger.info(f"Update Values: {values + condition_value}")

        db_conn.execute_query(
            query=query, data=tuple(values + condition_value), commit=self_commit
        )

        return FunctionResp(status=True)

    # UTILITY METHODS -------------------------------------------------------
    def gen_uid(self) -> str:
        """
        Generate a unique identifier for the row.
        """
        return str(uuid.uuid4())

    def to_dict(self) -> dict:
        """
        Convert the model to a dictionary.
        """
        return self.model_dump(exclude_unset=True)

    def to_json(self) -> str:
        """
        Convert the model to a JSON string.
        """
        return self.model_dump_json(exclude_unset=True)


############ EXAMPLE USAGE ############
# class User(BaseTableModel):
#     name: str = Column()
#     email: str = Column(unique=True)
#     age: int = Column()
#     is_active: bool = Column(default=True)
#     created_at: datetime.datetime = Column(is_timezone_aware=True)
#     updated_at: datetime.datetime = Column(is_timezone_aware=True)
#     hobbies: List[str] = Column(default=[])
#     company_id: str = Column(foreign_key_table="company", foreign_key_column="company_id") # foreign key

# # Generate DDL query ---
# User.generate_ddl_query()

# # Generate DML query ---
# user = User(name="John Doe", email="aa@s.com", age=25, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())

# # Get table name ---
# User.get_table_name()

# # Get column names ---
# User.get_columns()

# # Get primary key columns ---
# User.get_primary_keys()

# # Get foreign key columns ---
# User.get_foreign_keys()

# # Generate unique identifier ---
# user.gen_uid()
