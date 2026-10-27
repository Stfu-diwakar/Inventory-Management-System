"""
Database Connection and Execution Layer for Oracle SQL Database.
Uses 'oracledb' library in thin mode (no client install needed).
"""

import oracledb
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from config import DB_CONFIG

class OracleDatabaseManager:
    """Singleton manager for Oracle SQL database connections and queries."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OracleDatabaseManager, cls).__new__(cls)
            cls._instance.config = DB_CONFIG
        return cls._instance

    def update_config(self, user: str, password: str, host: str, port: int, service_name: str):
        """Update connection parameters dynamically from the UI."""
        self.config.USER = user
        self.config.PASSWORD = password
        self.config.HOST = host
        self.config.PORT = int(port)
        self.config.SERVICE_NAME = service_name

    def get_connection(self):
        """Returns a new live connection to Oracle Database."""
        return oracledb.connect(
            user=self.config.USER,
            password=self.config.PASSWORD,
            host=self.config.HOST,
            port=self.config.PORT,
            service_name=self.config.SERVICE_NAME
        )

    def test_connection(self) -> Dict[str, Any]:
        """Tests the Oracle connection and returns diagnostic info."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1")
                banner_row = cursor.fetchone()
                db_banner = banner_row[0] if banner_row else "Oracle Database"
                
                cursor.execute("SELECT COUNT(*) FROM user_tables")
                table_count = cursor.fetchone()[0]

                return {
                    "success": True,
                    "message": "Connected successfully to Oracle Database!",
                    "version": conn.version,
                    "banner": db_banner,
                    "table_count": table_count,
                    "dsn": self.config.dsn,
                    "user": self.config.USER
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "version": None,
                "banner": None,
                "table_count": 0,
                "dsn": self.config.dsn,
                "user": self.config.USER
            }

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None, as_dataframe: bool = True):
        """Executes a SELECT query and returns rows or a Pandas DataFrame."""
        params = params or {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                if as_dataframe:
                    return pd.DataFrame(rows, columns=columns)
                else:
                    return {"columns": columns, "rows": rows}
        except Exception as e:
            raise RuntimeError(f"Oracle SQL Query Error: {e}")

    def execute_dml(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Executes an INSERT, UPDATE, or DELETE statement and commits."""
        params = params or {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                rowcount = cursor.rowcount
                conn.commit()
                return rowcount
        except Exception as e:
            raise RuntimeError(f"Oracle SQL DML Error: {e}")

    def execute_dml_returning(self, sql: str, params: Optional[Dict[str, Any]] = None, out_var_type=oracledb.NUMBER):
        """Executes an INSERT with RETURNING clause to get generated ID."""
        params = params or {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                out_val = cursor.var(out_var_type)
                params["out_id"] = out_val
                cursor.execute(sql, params)
                conn.commit()
                return out_val.getvalue()[0] if isinstance(out_val.getvalue(), list) else out_val.getvalue()
        except Exception as e:
            raise RuntimeError(f"Oracle SQL Returning Error: {e}")

    def execute_script(self, sql_script: str) -> List[str]:
        """
        Executes a multi-statement SQL script.
        Splits statements by semicolon or slash block.
        """
        results = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Clean comments and split
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            for stmt in statements:
                if stmt.upper().startswith("SET ") or stmt.upper().startswith("SHOW "):
                    continue
                try:
                    cursor.execute(stmt)
                    results.append(f"SUCCESS: {stmt[:60]}...")
                except Exception as e:
                    results.append(f"ERROR: {stmt[:60]}... -> {str(e)}")
            conn.commit()
        return results

    def call_stock_movement_procedure(
        self, product_id: int, warehouse_id: int, transaction_type: str,
        quantity: int, reference_id: str, notes: str, performed_by: str = "APP_USER"
    ) -> Tuple[bool, str]:
        """Calls the SP_PROCESS_STOCK_MOVEMENT PL/SQL procedure."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                status_var = cursor.var(oracledb.STRING)
                msg_var = cursor.var(oracledb.STRING)

                cursor.callproc(
                    "SP_PROCESS_STOCK_MOVEMENT",
                    [product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by, status_var, msg_var]
                )
                conn.commit()
                status = status_var.getvalue()
                msg = msg_var.getvalue()
                return (status == "SUCCESS", msg or "Procedure executed.")
        except Exception as e:
            return (False, f"PL/SQL Call Exception: {str(e)}")

    def call_transfer_procedure(
        self, product_id: int, from_wh_id: int, to_wh_id: int,
        quantity: int, reference_id: str, notes: str, performed_by: str = "APP_USER"
    ) -> Tuple[bool, str]:
        """Calls the SP_TRANSFER_STOCK PL/SQL procedure."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                status_var = cursor.var(oracledb.STRING)
                msg_var = cursor.var(oracledb.STRING)

                cursor.callproc(
                    "SP_TRANSFER_STOCK",
                    [product_id, from_wh_id, to_wh_id, quantity, reference_id, notes, performed_by, status_var, msg_var]
                )
                conn.commit()
                status = status_var.getvalue()
                msg = msg_var.getvalue()
                return (status == "SUCCESS", msg or "Procedure executed.")
        except Exception as e:
            return (False, f"PL/SQL Transfer Exception: {str(e)}")

# Global database manager instance
db = OracleDatabaseManager()
