from contextlib import contextmanager
from sqlalchemy import Engine, MetaData, Table, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import APIRouter

from fastapi_booster import logger
from fastapi_booster.ModuleManager import ModuleManager


class Module:
    """
    A base class for creating modules in the FastAPI Booster framework.

    This class provides functionality for managing database connections,
    handling API routes, and managing module metadata.

    Attributes:
        name (str): The name of the module.
        description (str): A brief description of the module's purpose.

    Args:
        name (str): The name of the module.
        description (str): A brief description of the module's purpose.
        sql_url (str, optional): The SQL connection URL. Defaults to "sqlite:///.db".

    Raises:
        ValueError: If a module with the same name already exists.
    """

    def __init__(
        self,
        name: str,
        description: str,
        sql_url: str = "sqlite:///.db",
    ):
        # Get the module manager instance
        module_manager = ModuleManager.get_instance()

        # Check if the module already exists
        if module_manager.modules.get(name):
            module_manager.modules[name] = self

        # Initialize the module
        self.name: str = name
        self.description: str = description

        # Initialize the database objects
        self._model = declarative_base()
        self._sql_url: str = sql_url
        self._sql_engine: Engine = create_engine(sql_url)
        self._sql_session = sessionmaker(
            autocommit=False, autoflush=True, bind=self._sql_engine
        )
        self._metadata: MetaData = self._model.metadata

        # Initialize the API router
        self._router = APIRouter()

        # Add the module to the module manager
        module_manager.modules[self.name] = self

    def update_all_tables_schema(self):

        # get metadata from the database
        metadata = MetaData()
        metadata.reflect(bind=self._sql_engine)

        # sort tables by foreign key dependencies
        defined_tables = self._metadata.sorted_tables
        for table in defined_tables:
            if table.name not in metadata.tables:
                table.create(self._sql_engine, checkfirst=True)
                logger.info(f"\tTable {table.name} created in the database")
            else:
                if table.compare(metadata.tables[table.name]):
                    continue
                else:
                    logger.info(f"\tTable {table.name} already exists but differs from the defined schema.")

    def _foreign_keys_changed(self, new_column, existing_column):
        """
        Checks if the foreign keys of a column have changed.

        Args:
            new_column: The new column definition.
            existing_column: The existing column in the database.

        Returns:
            bool: True if foreign keys have changed, False otherwise.
        """
        new_fks = {fk.target_fullname for fk in new_column.foreign_keys}
        existing_fks = {fk.target_fullname for fk in existing_column.foreign_keys}
        return new_fks != existing_fks

    @contextmanager
    def db_session(self):
        """
        A context manager for database sessions.

        Yields:
            Session: A SQLAlchemy session object.

        Raises:
            Exception: If there's an error during the session.
        """
        db: Session = self._sql_session()
        try:
            yield db
        finally:
            db.close()

    def db(self):
        """
        A generator for database sessions.

        Yields:
            Session: A SQLAlchemy session object.
        """
        db = self._sql_session()
        try:
            yield db
        finally:
            db.close()

    @property
    def router(self):
        """
        Gets the FastAPI router for this module.

        Returns:
            APIRouter: The FastAPI router associated with this module.
        """
        return self._router

    @property
    def model(self):
        """
        Gets the SQLAlchemy model base for this module.

        Returns:
            DeclarativeMeta: The SQLAlchemy declarative base for defining models.
        """
        return self._model

