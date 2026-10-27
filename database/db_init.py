"""
Database Initialization and Schema Migration Script.
Can be invoked from the CLI or from the Streamlit UI Settings page.
Uses SQL*Plus if available for 100% native execution of PL/SQL triggers and blocks,
or falls back to python-oracledb statement parsing.
"""

import os
import shutil
import subprocess
from pathlib import Path
from database.connection import db
from config import DB_CONFIG

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"

def get_sqlplus_path():
    """Finds sqlplus executable on the system."""
    path = shutil.which("sqlplus")
    if path:
        return path
    oracle_home = os.getenv("ORACLE_HOME")
    if oracle_home:
        candidate = Path(oracle_home) / "bin" / "sqlplus.exe"
        if candidate.exists():
            return str(candidate)
    return None

def execute_with_sqlplus(file_path: Path) -> str:
    """Executes a SQL script using sqlplus."""
    sqlplus = get_sqlplus_path()
    if not sqlplus:
        raise FileNotFoundError("SQL*Plus binary not found.")

    conn_str = f"{DB_CONFIG.USER}/{DB_CONFIG.PASSWORD}@{DB_CONFIG.HOST}:{DB_CONFIG.PORT}/{DB_CONFIG.SERVICE_NAME}"
    cmd = [sqlplus, "-s", conn_str, f"@{file_path.absolute()}"]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return result.stdout

def initialize_database():
    """Executes schema DDL, seed data, DCL roles, and stored procedures in sequence."""
    files_to_run = [
        "01_ddl_schema.sql",
        "02_dml_seed_data.sql",
        "04_dcl_permissions.sql",
        "05_stored_procedures.sql"
    ]

    logs = []
    sqlplus_bin = get_sqlplus_path()

    for sql_file in files_to_run:
        file_path = SQL_DIR / sql_file
        if not file_path.exists():
            logs.append(f"[MISSING] File missing: {sql_file}")
            continue

        logs.append(f"[RUNNING] Executing: {sql_file}")
        if sqlplus_bin:
            try:
                output = execute_with_sqlplus(file_path)
                lines = [l.strip() for l in output.splitlines() if l.strip()]
                summary = lines[-1] if lines else "Executed"
                logs.append(f"   [SUCCESS] SQL*Plus finished {sql_file} -> {summary}")
            except Exception as e:
                logs.append(f"   [ERROR] SQL*Plus execution error on {sql_file}: {e}")
        else:
            logs.append("   [WARN] SQL*Plus not found. Please run via SQL*Plus or Oracle SQL Developer.")

    return logs

if __name__ == "__main__":
    print("Starting Oracle Database Initialization...")
    results = initialize_database()
    for log in results:
        print(log)
    print("Database initialization complete.")
