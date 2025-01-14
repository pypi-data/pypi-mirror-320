from os import getcwd, path, makedirs
from flask import Flask
from flask_migrate import Migrate, migrate, upgrade, init, stamp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from contextlib import contextmanager
from colorama import init as colorama_init, Fore, Style
from src_IFP.config.config import Config

colorama_init(autoreset=True)

class Database_config(Config):
    """
    Database configuration class that handles database initialization, migrations and upgrades.
    Prevents duplicate database creation and ensures correct database location.
    """
    
    MIGRATIONS_PATH = 'database/migrations'
    _setup_completed = False  # Class variable to track setup state

    def __init__(self, app: Flask) -> None:
        """
        Initialize database configuration with Flask application.
        
        Args:
            app (Flask): Flask application instance
            
        Raises:
            ValueError: If app is not properly configured
        """
        super().__init__()
        self.__app: Flask = app
        self.__app_db: SQLAlchemy = SQLAlchemy(app)
        self.__migration = Migrate(app, self.__app_db, directory=self.MIGRATIONS_PATH)
        self.__initial_setup_done = False

    @property
    def app_db(self) -> SQLAlchemy:
        """Get SQLAlchemy instance."""
        return self.__app_db

    @property
    def migration(self) -> Migrate:
        """Get Migrate instance."""
        return self.__migration

    @contextmanager
    def __error_handling(self, operation: str):
        """Context manager for consistent error handling."""
        try:
            yield
        except Exception as e:
            print(f"{Fore.RED}Error during {operation}: {str(e)}{Style.RESET_ALL}")
            raise RuntimeError(f"Error in {operation}: {str(e)}") from e

    def __normalize_db_path(self, uri: str) -> str:
        """
        Normalize database path to ensure it's in the correct location.
        
        Args:
            uri (str): Original database URI
            
        Returns:
            str: Normalized database URI
        """
        if uri.startswith('sqlite:///'):
            # Extract the path part from the URI
            db_path = uri[10:]
            if not path.isabs(db_path):
                # If it's a relative path, make it absolute from project root
                project_root = getcwd()
                db_dir = path.join(project_root, 'database')
                if not path.exists(db_dir):
                    makedirs(db_dir)
                db_path = path.join(db_dir, path.basename(db_path))
                uri = f'sqlite:///{db_path}'
            
            # Ensure the directory exists
            db_dir = path.dirname(db_path)
            if not path.exists(db_dir):
                makedirs(db_dir)

        return uri

    def __validate_uri(self, uri: str) -> str:
        """
        Validate and normalize database URI string.
        
        Args:
            uri (str): Database URI to validate
            
        Returns:
            str: Normalized URI
            
        Raises:
            ValueError: If URI is invalid
        """
        if not isinstance(uri, str):
            raise ValueError('Database URI must be string')
        if not uri:
            raise ValueError('Database URI cannot be empty')
        
        return self.__normalize_db_path(uri)

    def __ensure_database_exists(self, uri: str) -> bool:
        """
        Ensure database exists in the correct location.
        
        Args:
            uri (str): Normalized database URI
            
        Returns:
            bool: True if database was created, False if it already existed
        """
        if not database_exists(uri):
            print(f"{Fore.YELLOW}Database does not exist. Creating at {uri}...{Style.RESET_ALL}")
            with self.__error_handling("database creation"):
                create_database(uri)
            print(f"{Fore.GREEN}Database created successfully{Style.RESET_ALL}")
            return True
        print(f"{Fore.BLUE}Database already exists at {uri}{Style.RESET_ALL}")
        return False

    def __handle_migrations(self, migrations_dir: str, is_new_database: bool) -> None:
        """Handle all migration operations in a single method."""
        # Initialize migrations if necessary
        if not path.exists(migrations_dir):
            print(f"{Fore.YELLOW}Migrations not initialized. Running `init`...{Style.RESET_ALL}")
            with self.__error_handling("migrations initialization"):
                init(self.__migration.directory)  # flask db init
                migrate(self.__migration.directory)  # flask db migrate
            print(f"{Fore.GREEN}Migrations initialized successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}Checking for model changes...{Style.RESET_ALL}")
            with self.__error_handling("migrations update"):
                migrate(self.__migration.directory)  # flask db migrate
            print(f"{Fore.GREEN}Migration files updated{Style.RESET_ALL}")
        
        # Apply migrations
        print(f"{Fore.YELLOW}Applying pending migrations...{Style.RESET_ALL}")
        with self.__error_handling("applying migrations"):
            upgrade(self.__migration.directory)  # flask db upgrade
        print(f"{Fore.GREEN}Migrations applied successfully{Style.RESET_ALL}")

    def setup(self) -> None:
        """
        Configure database and migrations in production environment.
        Ensures single database creation and correct database location.
        """
        # Skip if already completed setup in this Flask instance
        if Database_config._setup_completed:
            print(f"{Fore.BLUE}Database setup already completed, skipping...{Style.RESET_ALL}")
            return

        uri = self.__app.config.get('SQLALCHEMY_DATABASE_URI')
        if not uri: 
            raise ValueError('SQLALCHEMY_DATABASE_URI is not defined')

        # Validate and normalize the database URI
        uri = self.__validate_uri(uri)
        # Update the app config with the normalized URI
        self.__app.config['SQLALCHEMY_DATABASE_URI'] = uri

        if self.__app.config['FLASK_ENV'] != 'production':
            print(f"{Fore.YELLOW}Skipping database setup: not in production{Style.RESET_ALL}")
            return

        # Create database if needed (outside of app context)
        is_new_database = self.__ensure_database_exists(uri)

        # Handle all migration operations in a single app context
        with self.__app.app_context():
            migrations_dir = path.join(getcwd(), self.__migration.directory)
            self.__handle_migrations(migrations_dir, is_new_database)

        Database_config._setup_completed = True
        print(f"{Fore.GREEN}Database setup completed successfully{Style.RESET_ALL}")