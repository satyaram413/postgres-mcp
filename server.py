from mcp.server.fastmcp import FastMCP
import psycopg2
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Create MCP server
mcp = FastMCP(
    name="postgres",
    host="0.0.0.0",
    port=8000,
)

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://test:test@localhost:5438/aps")
print(DATABASE_URL)
def get_connection():
    return psycopg2.connect(DATABASE_URL)

@mcp.tool()
async def execute_select(query: str) -> Dict[str, Any]:
    """Execute a SELECT SQL query and return results.
    
    Args:
        query: SQL SELECT query to execute
    """
    if not query.strip().lower().startswith("select"):
        return {"error": "Only SELECT queries are allowed"}
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                return {
                    "columns": columns,
                    "rows": results,
                    "count": len(results)
                }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_schema() -> Dict[str, Any]:
    """Get database schema information (tables and columns)."""
    schema = {}
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Get all tables
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [row[0] for row in cur.fetchall()]
                
                for table in tables:
                    cur.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                    """, (table,))
                    columns = [{"name": row[0], "type": row[1]} for row in cur.fetchall()]
                    schema[table] = columns
        
        return schema
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def list_tables() -> Dict[str, Any]:
    """List all tables in the database."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_schema, table_name 
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY table_schema, table_name
                """)
                tables = [{"schema": row[0], "table": row[1]} for row in cur.fetchall()]
                
                return {
                    "tables": tables,
                    "count": len(tables)
                }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
