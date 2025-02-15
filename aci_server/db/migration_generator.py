import inspect
import os
from datetime import datetime
from pathlib import Path
from typing import Type
from uuid import UUID
from supabase import create_client
from dotenv import load_dotenv
from .models import SupabaseModel

load_dotenv()

def generate_create_table_sql(model: Type[SupabaseModel]) -> str:
    fields = model.__fields__
    table_name = model.Config.table_name
    
    columns = []
    for name, field in fields.items():
        sql_type = _get_sql_type(field.annotation)
        nullable = "NOT NULL" if field.is_required else "NULL"
        columns.append(f"    {name} {sql_type} {nullable}")
    
    columns_sql = ",\n".join(columns)
    return f"""
CREATE TABLE IF NOT EXISTS {table_name} (
{columns_sql}
);
"""

def _get_sql_type(py_type: type) -> str:
    type_mapping = {
        str: "TEXT",
        int: "INTEGER",
        float: "REAL",
        bool: "BOOLEAN",
        UUID: "UUID",
        datetime: "TIMESTAMP",
    }
    return type_mapping.get(py_type, "TEXT")

def apply_migration_to_supabase(sql_content: str):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not (supabase_url and supabase_key):
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
    
    supabase = create_client(supabase_url, supabase_key)
    try:
        result = supabase.rpc('exec', {"sql": sql_content}).execute()
        if result.error:
            raise Exception(f"Migration failed: {result.error.message}")
        print("Migration applied successfully")
    except Exception as e:
        print(f"Error applying migration: {str(e)}")
        raise

def create_migration():
    from . import models
    model_classes = [
        cls for _, cls in inspect.getmembers(models, inspect.isclass)
        if issubclass(cls, SupabaseModel) and cls != SupabaseModel
    ]

    migrations_dir = Path(__file__).parent / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_file = migrations_dir / f"{timestamp}_create_tables.sql"
    
    sql_contents = []
    for model in model_classes:
        sql_contents.append(generate_create_table_sql(model))
    
    full_sql = "\n".join(sql_contents)
    
    with open(migration_file, "w") as f:
        f.write(full_sql)
    
    apply_migration_to_supabase(full_sql)
    
    print(f"Created and applied migration: {migration_file}")

if __name__ == "__main__":
    create_migration()