from typing import *
import warnings
import pandas as pd
import snowflake.connector
import psycopg2
import psycopg2.extras
import pymysql
import pymssql
# import cx_Oracle
from snowflake.connector.pandas_tools import write_pandas
import datetime as dt

__all__ = ["DBConnector"]


class DBConnector:
    def __init__(
        self,
        dbms: str,
        user: str,
        pw: str,
        dbname: str,
        role: Optional[str] = None,
        warehouse: Optional[str] = None,
        host: str = "localhost",
        port: Optional[int] = None,
        account: Optional[str] = None,
    ) -> None:
        self.dbms = dbms.lower()  # 'pg' for PostgreSQL, 'sf' for Snowflake, 'mysql' for MySQL, 'mssql' for SQL Server, 'oracle' for Oracle
        self._con = None
        self._user = user
        self._password = pw
        self._dbname = dbname
        self._host = host
        self._port = port or self._default_port()
        self._role = role
        self._warehouse = warehouse
        self._account = account
        self._init_connection()

    def _default_port(self):
        if self.dbms == "pg":
            return 5432
        elif self.dbms == "sf":
            return None
        elif self.dbms == "mysql":
            return 3306
        elif self.dbms == "mssql":
            return 1433
        elif self.dbms == "oracle":
            return 1521
        else:
            raise ValueError("Unsupported DBMS. Use 'pg', 'sf', 'mysql', 'mssql', or 'oracle'.")

    def _init_connection(self):
        if self.dbms == "pg":
            self._con = psycopg2.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                dbname=self._dbname,
                port=self._port,
            )
        elif self.dbms == "sf":
            self._con = snowflake.connector.connect(
                account=self._account,
                user=self._user,
                password=self._password,
                role=self._role,
                database=self._dbname,
                warehouse=self._warehouse,
            )
        elif self.dbms == "mysql":
            self._con = pymysql.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._dbname,
                port=self._port,
            )
        elif self.dbms == "mssql":
            self._con = pymssql.connect(
                server=self._host,
                user=self._user,
                password=self._password,
                database=self._dbname,
                port=self._port,
            )
        # elif self.dbms == "oracle":
        #     dsn = cx_Oracle.makedsn(self._host, self._port, service_name=self._dbname)
        #     self._con = cx_Oracle.connect(user=self._user, password=self._password, dsn=dsn)
        else:
            raise ValueError("Unsupported DBMS. Use 'pg', 'sf', 'mysql', 'mssql', or 'oracle'.")

    def _validate(self):
        if self.dbms == "pg" and self._con.closed:
            self._init_connection()
        elif self.dbms == "sf" and self._con.is_closed():
            self._init_connection()
        elif self.dbms == "mysql" and self._con is None:
            self._init_connection()
        elif self.dbms == "mssql" and self._con._conn.closed:
            self._init_connection()
        elif self.dbms == "oracle" and not self._con.ping():
            self._init_connection()

    def read_to_df(self, query: str, retry: int = 3) -> pd.DataFrame:
        """Executes a SELECT query and returns the result as a DataFrame."""
        for attempt in range(retry):
            try:
                self._validate()
                print(f"Selection Query:\n{query}")
                if self.dbms in ["pg", "mysql", "mssql", "oracle"]:
                    with self._con.cursor() as cur:
                        cur.execute(query)

                        # Debugging: Check cursor description and fetched rows
                        if cur.description is None:
                            raise ValueError("Query executed, but no result set returned.")
                        
                        rows = cur.fetchall()
                        columns = [desc[0] for desc in cur.description]
                        print(f"Fetched {len(rows)} rows with columns: {columns}")

                        # Create DataFrame
                        data = pd.DataFrame(rows, columns=columns)
                elif self.dbms == "sf":
                    with self._con.cursor() as cur:
                        cur.execute(query)
                        data = cur.fetch_pandas_all()
                        
                return data
            except Exception as e:
                warnings.warn(f"Attempt {attempt + 1}: Query failed with error: {e}")
                self._validate()
        raise RuntimeError("Max retries reached for read_to_df.")

    def execution_query(self, query: str, retry: int = 3) -> bool:
        """Executes a DML query and commits the changes."""
        for attempt in range(retry):
            try:
                self._validate()
                with self._con.cursor() as cur:
                    print(f"Execution Query:\n{query}")
                    cur.execute(query)
                self._con.commit()
                print("Commit Success!")
                return True
            except Exception as e:
                warnings.warn(f"Attempt {attempt + 1}: Execution failed with error: {e}")
                self._con.rollback()
                self._validate()
        raise RuntimeError("Max retries reached for execution_query.")

    def insert_df(self, df: pd.DataFrame, table: str, schema: str = "public", retry: int = 3) -> bool:
        """
        Inserts a pandas DataFrame into a database table.
        
        Caution
        - df의 컬럼명과 Insert 대상 테이블 컬럼명 동일한 지 확인
        - Insert 대상의 table 정보 정확하게 입력(schema,tbName)
        참고사항
        - chunk_size는 default 100000으로 설정. 작업에 따라 명시해서 사용 권장
        - snowflake의 경우 아래 구문이 먼저 실행된 이후 df가 insert됨
            `USE SCHEMA {schema};`
            `ALTER SESSION SET AUTOCOMMIT=TRUE;`   
        - postgres의 경우 성능이 가장 뛰어난 extras.execute_values 사용
        """
        for attempt in range(retry):
            try:
                self._validate()
                if self.dbms == "pg":
                    tuples = [tuple(x) for x in df.to_numpy()]
                    cols = ",".join(df.columns)
                    query = f"INSERT INTO {schema}.{table} ({cols}) VALUES %s"
                    with self._con.cursor() as cur:
                        psycopg2.extras.execute_values(cur, query, tuples)
                    self._con.commit()
                elif self.dbms == "mysql":
                    tuples = [tuple(x) for x in df.to_numpy()]
                    cols = ",".join(df.columns)
                    placeholders = ",".join(["%s"] * len(df.columns))
                    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
                    with self._con.cursor() as cur:
                        cur.executemany(query, tuples)
                    self._con.commit()
                elif self.dbms == "mssql":
                    tuples = [tuple(x) for x in df.to_numpy()]
                    cols = ",".join(df.columns)
                    placeholders = ",".join(["%s"] * len(df.columns))
                    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
                    with self._con.cursor() as cur:
                        cur.executemany(query, tuples)
                    self._con.commit()
                # elif self.dbms == "oracle":
                #     tuples = [tuple(x) for x in df.to_numpy()]
                #     cols = ",".join(df.columns)
                #     placeholders = ",".join([":" + str(i + 1) for i in range(len(df.columns))])
                #     query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
                #     with self._con.cursor() as cur:
                #         cur.executemany(query, tuples)
                #     self._con.commit()
                elif self.dbms == "sf":
                    df.columns = df.columns.str.upper()
                    write_pandas(self._con, df, table_name=table.upper(), schema=schema.upper())
                return True
            except Exception as e:
                warnings.warn(f"Attempt {attempt + 1}: Insert failed with error: {e}")
                self._con.rollback()
                self._validate()
        raise RuntimeError("Max retries reached for insert_df.")

    def close(self):
        """Closes the database connection."""
        if self._con:
            if self.dbms == "pg" and not self._con.closed:
                self._con.close()
            elif self.dbms == "sf" and not self._con.is_closed():
                self._con.close()
            elif self.dbms == "mysql" and self._con is None:
                self._con.close()
            elif self.dbms == "mssql" and not self._con._conn.closed:
                self._con.close()
            elif self.dbms == "oracle" and self._con:
                self._con.close()

    def __del__(self):
        self.close()
