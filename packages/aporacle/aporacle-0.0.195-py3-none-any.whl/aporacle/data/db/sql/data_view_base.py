import logging
import os

from komoutils.core import KomoBase
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


class DataViewBase(KomoBase):
    def __init__(self):
        # Get database credentials from environment variables
        self.db_name = os.getenv('DB_NAME', 'ftsodb')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', 'example')
        self.db_host = os.getenv('DB_HOST', '127.0.0.1')
        self.db_port = os.getenv('DB_PORT', '3306')

        # Create the fully formed db_urls for SQLAlchemy
        self.db_url = f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.async_db_url = f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

        # Create sync engine and session (default)
        self.engine = create_engine(self.db_url)
        self.session = sessionmaker(bind=self.engine)

        # Create async engine and session (optional)
        self.async_engine = create_async_engine(self.async_db_url)
        self.async_session = sessionmaker(bind=self.async_engine, class_=AsyncSession)

        self.check_database_and_credentials()

    def check_database_and_credentials(self):
        try:
            with self.engine.connect() as connection:
                # Check if the database exists
                result = connection.execute(text(f"SHOW DATABASES LIKE '{self.db_name}'"))
                if result.fetchone():
                    self.log_with_clock(log_level=logging.INFO, msg=f"Database '{self.db_name}' exists.")
                    
                    # Check if credentials are valid by attempting to use the database
                    connection.execute(text(f"USE {self.db_name}"))
                    connection.execute(text("SELECT 1"))
                    self.log_with_clock(log_level=logging.INFO, msg="Database credentials are valid.")
                    return True
                else:
                    self.log_with_clock(log_level=logging.WARNING, msg=f"Database '{self.db_name}' does not exist.")
                    return False
        except SQLAlchemyError as e:
            self.log_with_clock(log_level=logging.ERROR, msg=f"Error checking database or credentials: {str(e)}")
            return False

    def check_db_connection(self):
        try:
            with self.session() as session:
                session.execute(text("SELECT 1"))
            self.log_with_clock(log_level=logging.INFO, msg="Database connection successful.")
            return True
        except SQLAlchemyError as e:
            self.log_with_clock(log_level=logging.ERROR, msg=f"Error connecting to the database: {str(e)}")
            return False

    async def check_async_db_connection(self):
        try:
            async with self.async_session() as session:
                await session.execute(text("SELECT 1"))
            self.log_with_clock(log_level=logging.INFO, msg="Async database connection successful.")
            return True
        except SQLAlchemyError as e:
            self.log_with_clock(log_level=logging.ERROR, msg=f"Error connecting to the async database: {str(e)}")
            return False

