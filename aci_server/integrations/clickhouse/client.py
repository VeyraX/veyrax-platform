import clickhouse_driver
from typing import Dict, Any, List, Optional, Union, Tuple


class ClickHouseClient:
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params.copy()
        
        host = self.connection_params.get('host', '')
        if '.clickhouse.cloud' in host:
            self.connection_params['secure'] = True
                
        self.client = None

    def connect(self):
        if self.client is None:
            host = self.connection_params.get('host', 'localhost')
            port = self.connection_params.get('port', 9000)
            if isinstance(port, str):
                port = int(port)
            database = self.connection_params.get('dbname', 'default')
            user = self.connection_params.get('user', 'default')
            password = self.connection_params.get('password', '')
            secure = self.connection_params.get('secure', False)
            
            print(f"Connecting to ClickHouse at {host}:{port} (secure={secure})")
            
            self.client = clickhouse_driver.Client(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                secure=secure,
                verify=False,
                settings={'use_numpy': False}
            )

    def disconnect(self):
        self.client = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            self.connect()
            print(f"Executing query: {query}")
            
            result, columns = self.client.execute(
                query, 
                params or {}, 
                with_column_types=True
            )
            
            column_names = [col[0] for col in columns]
            rows = []
            for row in result:
                rows.append(dict(zip(column_names, row)))
            
            return rows
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            raise Exception(error_msg)
        finally:
            pass

    def get_tables(self) -> List[Dict[str, Any]]:
        database = self.connection_params.get('dbname', 'default')
        print(f"Getting tables from {database}")
        query = f"SHOW TABLES FROM `{database}`"
            
        result = self.execute_query(query)
        
        return result

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        database = self.connection_params.get('dbname', 'default')
        query = f"DESCRIBE TABLE `{database}`.`{table_name}`"
        return self.execute_query(query)
