"""
Utility file for any DB related actions
"""

import os
from typing import Any, Type, Union

import pandas as pd
import psycopg2 as psycopg

from uniteampckg.models.base_models import FunctionResp
from uniteampckg.utils.logging.logger import Logger

logger = Logger("DbUtil")
logger.configure_logging()

ConnectionType: Type[psycopg.extensions.connection] = psycopg.extensions.connection


class DbUtil:
    """
    TODO
    """

    connection: Type[psycopg.extensions.connection] = None

    def __init__(self):
        """
        TODO
        """
        self.connection_params = {
            "host": os.getenv("DATABASE_HOST"),
            "database": os.getenv("DATABASE_NAME"),
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASS"),
            "port": os.getenv("DATABASE_PORT"),
        }
        self.connection = None

    def connect(self, default_schema: str = None) -> FunctionResp:
        """
        TODO
        """
        try:
            if default_schema:
                resp = self.create_schema(default_schema)
                if resp.status is False:
                    raise RuntimeError("Failed to create Schema")
                self.connection_params["options"] = f"-c search_path={ default_schema}"

            # Establish the connection
            self.connection = psycopg.connect(**self.connection_params)

            return FunctionResp(status=True)
        except Exception as error:
            logger.error(
                "DB: Error creating connection ",
                exception=str(error),
            )
            return FunctionResp(
                status=False,
                error_message="Failed to create DB Connection",
            )

    def disconnect(self, do_commit=False):
        """
        TODO
        """
        try:
            if self.connection:
                if do_commit:
                    self.commit()
                self.connection.close()
        except BaseException:
            pass

    def commit(self) -> FunctionResp:
        """
        Commits the current connection changes.\n If not success full, returns status->false
        """
        try:
            if self.connection:
                self.connection.commit()
                return FunctionResp(status=True)

            raise Exception("No connection found to commit")
        except Exception as error:
            return FunctionResp(status=False)

    def create_schema(self, schema: str):
        """
        TODO
        """
        try:
            # Connect to the database if the connection is not established
            if not self.connection:
                self.connect()

            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

            # Commit the transaction
            self.connection.commit()
            return FunctionResp(status=True)
        except RuntimeError as error:
            # Rollback the transaction in case of an error
            self.connection.rollback()
            return FunctionResp(
                status=False,
                error_message=f"Failed to create Schema: {schema}",
            )

    def execute_query(
        self,
        query,
        table_name=None,
        as_pd=False,
        data: tuple = None,
        table_schema=None,
        commit=False,
        no_fetch=False,
        get_column_names=False,
    ) -> FunctionResp[Union[None, dict, list, pd.DataFrame]]:
        """
        Query execution function. Capable of all query type. For insert query,
        pass input through @param(data) as tuple. To retrive result as Datafarme, set @param(as_pd) true,\n
        pass @param(commit) true for commiting the execution. \n
        Pass the @(table_schema) to connect to a particualr schema (only if connection obj is not defined already).\n
        @param(no_fetch) can be used to skip the result fetching, and just carryout the execution.
        """
        if not self.connection:
            conresp = self.connect(table_schema)
            if not conresp.status:
                raise RuntimeError("Failed to create connection")

        try:
            with self.connection.cursor() as cursor:
                if data is not None:
                    cursor.execute(query, data)
                else:
                    cursor.execute(query)

                if commit is True:
                    if not self.commit().status:
                        #! Failed to commit
                        raise Exception("Failed to commit the result")

                if no_fetch is True:
                    # Dont fetch the result, probably its a INSERT or UPDATE
                    # query
                    return FunctionResp(status=True)

                result = cursor.fetchall()

                if as_pd:
                    column_names = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(result, columns=column_names)

                    if len(df.index) == 0:
                        return FunctionResp[pd.DataFrame](
                            status=True, status_code=204, data=df
                        )
                    return FunctionResp[pd.DataFrame](
                        status=True, status_code=200, data=df
                    )

                if get_column_names:
                    column_names = [desc[0] for desc in cursor.description]
                    output_list_dict = []
                    for i, row in enumerate(result):
                        output_list_dict.append(dict(zip(column_names, row)))

                    return FunctionResp[list](
                        status=True, status_code=200, data=output_list_dict
                    )

                return FunctionResp[list](status=True, status_code=200, data=result)

        except RuntimeError as error:
            logger.error("DB: Error executing query", exception=error)
            return FunctionResp(status=False, error_message="")
        except Exception as error:
            logger.error(f"DB: Error executing query {type(error)} ", exception=error)
            return FunctionResp(status=False, error_message="")
