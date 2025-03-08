import psycopg2
from psycopg2 import sql
from typing import Dict, Any, List, Optional, Union, Tuple


class PostgreSQLClient:
    def __init__(self, connection_params: Dict[str, Any]):
        self.schema = connection_params.pop('schema', 'public')
        
        self.connection_params = {k: v for k, v in connection_params.items() 
                                if k in ['host', 'port', 'dbname', 'user', 'password']}
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        try:
            self.connect()
            self.cursor.execute(query)
            if self.cursor.description:
                columns = [desc[0] for desc in self.cursor.description]
                results = []
                for row in self.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            
            self.conn.commit()
            return []
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def get_tables(self) -> List[Dict[str, Any]]:
        query = f"""
        SELECT 
            table_name, 
            table_type,
            obj_description(pgc.oid, 'pg_class') as table_description
        FROM 
            information_schema.tables t
        JOIN 
            pg_catalog.pg_class pgc ON t.table_name = pgc.relname
        WHERE 
            table_schema = '{self.schema}'
        ORDER BY 
            table_name;
        """
        return self.execute_query(query)

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        query = f"""
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default,
            pg_catalog.col_description(
                format('%I.%I', table_schema, table_name)::regclass::oid, 
                ordinal_position
            ) as column_description
        FROM 
            information_schema.columns
        WHERE 
            table_schema = '{self.schema}' AND table_name = '{table_name}'
        ORDER BY 
            ordinal_position;
        """
        return self.execute_query(query)
