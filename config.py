"""
Configuration module for the Oracle SQL Inventory Management System.
Supports environment variables with default values matching local Oracle 23ai/XE setup.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

@dataclass
class DatabaseConfig:
    USER: str = os.getenv("ORACLE_USER", "system")
    PASSWORD: str = os.getenv("ORACLE_PASSWORD", "")
    HOST: str = os.getenv("ORACLE_HOST", "localhost")
    PORT: int = int(os.getenv("ORACLE_PORT", "1521"))
    SERVICE_NAME: str = os.getenv("ORACLE_SERVICE_NAME", "FREEPDB1")

    @property
    def dsn(self) -> str:
        return f"{self.HOST}:{self.PORT}/{self.SERVICE_NAME}"

    def get_connection_dict(self):
        return {
            "user": self.USER,
            "password": self.PASSWORD,
            "host": self.HOST,
            "port": self.PORT,
            "service_name": self.SERVICE_NAME
        }

@dataclass
class AppConfig:
    APP_NAME: str = "ApexStock Enterprise"
    PROJECT_TITLE: str = "Inventory Management System (DBMS Project)"
    DATABASE_SYSTEM: str = "Oracle Database 23ai / 21c / 19c"
    VERSION: str = "2.5.0"
    THEME_PRIMARY_COLOR: str = "#2563EB"
    DEFAULT_PAGE_SIZE: int = 25

DB_CONFIG = DatabaseConfig()
APP_CONFIG = AppConfig()
