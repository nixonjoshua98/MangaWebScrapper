import sqlalchemy
import os

from .database_constants import *


class Database:
    """ Static class which creates and updates the database models, as well as storing a session factory
    for database connections """

    class DatabaseEngineError(Exception):
        pass

    engine = None
    session_factory = None

    @classmethod
    def create(cls) -> bool:
        from .database_models import Base

        # Create the database path if not already created
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        if cls.engine is None:  # Create the engine with debug (echo) off
            cls.engine = sqlalchemy.create_engine(CON_STR, echo=False)

        """ Database session factory which will be used in the context manager
        to connect to the database, <expire_on_commit> must be set to False otherwise
        the session factory becomes invalid after each commit(?)
        """
        if cls.session_factory is None:
            cls.session_factory = sqlalchemy.orm.sessionmaker(bind=cls.engine, expire_on_commit=False)

        # Create or update all of the models which was created in <database_models> using <Base>
        Base.metadata.create_all(cls.engine)

        return True


class DatabaseSession:
    """ Context manager for connecting to the database """
    def __init__(self):
        if Database.session_factory is None or Database.engine is None:
            raise Database.DatabaseEngineError("Database session or engine has not been initialised yet")

    def __enter__(self):
        self.session = sqlalchemy.orm.scoped_session(Database.session_factory)

        return self.session

    def __exit__(self, *args):
        #  Auto-commit and auto-flush can be enabled when creating the factory but I prefer to see the method calls
        self.session.commit()
        self.session.flush()
        self.session.close()
