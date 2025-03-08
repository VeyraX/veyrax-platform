import snowflake.connector
from typing import Dict, Any, List, Optional, Union, Tuple


class SnowflakeClient:
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.conn is None:   
            account = self.connection_params.get('account')
            user = self.connection_params.get('user')
            password = self.connection_params.get('password')
            warehouse = self.connection_params.get('warehouse')
            database = self.connection_params.get('database')
            schema = self.connection_params.get('schema')
            role = self.connection_params.get('role')
            
            self.conn = snowflake.connector.connect(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema,
                role=role
            )
            
            self.cursor = self.conn.cursor(snowflake.connector.DictCursor)

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if self.cursor.description:
                return self.cursor.fetchall()
            
            return []
        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def get_tables(self) -> List[Dict[str, Any]]:
        database = self.connection_params.get('database')
        schema = self.connection_params.get('schema')
        
        query = f"SHOW TABLES IN {database}.{schema}"
            
            
        return self.execute_query(query)

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        database = self.connection_params.get('database')
        schema = self.connection_params.get('schema')
        
        query = f"DESCRIBE TABLE {database}.{schema}.{table_name}"
            
        return self.execute_query(query)
