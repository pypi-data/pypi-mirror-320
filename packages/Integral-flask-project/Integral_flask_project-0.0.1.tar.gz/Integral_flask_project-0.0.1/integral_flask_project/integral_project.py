from enum import Enum
from os import PathLike, path
from typing import Any, Tuple, List
from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from src_IFP import App_config
from src_IFP.config.cors_config import CORS_manager

class Integral_flask_project(Flask):
    """
    A singleton Flask application wrapper that provides integrated functionality for web applications.
    Inherits from Flask and extends it with additional features for handling WebSockets, JWT,
    database management, email handling, and CORS configuration.

    Attributes:
        _instance: Singleton instance of the class
        __name: Application package name
        __run_type: Application run type (FLASK or SOCKET_IO)
        __blueprints: List of registered blueprints
        __path_routes: Directory path for route modules
        __path_sockets: Directory path for socket modules
        __app_config: Application configuration instance
        __cors: CORS manager instance
        __jwt: JWT manager instance
        __app_db: SQLAlchemy database instance
        __migration: Database migration manager
        __socket: SocketIO instance
        __mail: Mail manager instance
    """
    
    _instance = None

    class RUN_TYPE(Enum):
        """
        Defines the application run type.
        
        Attributes:
            SOKET_IO: Run application with WebSocket support
            FLASK: Run as standard Flask application
        """
        SOKET_IO = 'socket'
        FLASK = 'flask'

    def __new__(cls, 
                import_name: str,
                run_type: RUN_TYPE = RUN_TYPE.FLASK,
                env: object|str|None = None,
                path_routes:str = 'routes',
                path_sockets:str = 'sockets',
                static_url_path: str | None = None,
                static_folder: str | PathLike[str] | None = "static",
                static_host: str | None = None,
                host_matching: bool = False,
                subdomain_matching: bool = False,
                template_folder: str | PathLike[str] | None = "templates",
                instance_path: str | None = None,
                instance_relative_config: bool = False,
                root_path: str | None = None) -> 'Integral_flask_project':
        """
        Creates or returns the singleton instance of Integral_flask_project.
        
        Args:
            import_name: The name of the application package
            run_type: Determines if app runs with WebSocket support
            env: Environment configuration object or string
            path_routes: Directory path for route modules
            path_sockets: Directory path for socket modules
            static_url_path: URL path for static files
            static_folder: Directory containing static files
            static_host: Host for static files
            host_matching: Enable host matching for routes
            subdomain_matching: Enable subdomain matching
            template_folder: Directory containing templates
            instance_path: Path to instance folder
            instance_relative_config: Enable relative instance config
            root_path: Root path of the application
        
        Returns:
            Integral_flask_project: The singleton instance
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 import_name: str,
                 run_type: RUN_TYPE = RUN_TYPE.FLASK,
                 env: object|str|None = None,
                 path_routes:str = 'routes',
                 path_sockets:str = 'sockets',
                 static_url_path: str | None = None,
                 static_folder: str | PathLike[str] | None = "static",
                 static_host: str | None = None,
                 host_matching: bool = False,
                 subdomain_matching: bool = False,
                 template_folder: str | PathLike[str] | None = "templates",
                 instance_path: str | None = None,
                 instance_relative_config: bool = False,
                 root_path: str | None = None):
        """
        Initializes the Integral_flask_project instance.
        
        Args: Same as __new__
        """
        super().__init__(import_name, static_url_path, static_folder, static_host,
                        host_matching, subdomain_matching, template_folder,
                        instance_path, instance_relative_config, root_path)
        
        self.__name:str = import_name
        self.__run_type = run_type
        self.__blueprints: List[Tuple[Blueprint, dict]] = []

        self.__path_routes:str = path_routes
        self.__path_sockets:str = path_sockets 

        self.__app_config = App_config(self)
        self.__cors:CORS_manager = self.__app_config._cors

        self.__jwt, db, self.__socket, self.__mail = self.__app_config.create_app(env)
        self.__app_db, self.__migration, self.__database = db

    @property
    def cors(self) -> CORS_manager:
        """
        Get the CORS configuration manager.
        
        Returns:
            CORS_manager: Instance for managing CORS settings
        """
        return self.__cors

    @property
    def jwt(self) -> JWTManager:
        """
        Get the JWT manager for handling authentication.
        
        Returns:
            JWTManager: Instance for JWT operations
        """
        return self.__jwt
    
    @property
    def db(self) -> SQLAlchemy:
        """
        Get the SQLAlchemy database instance.
        
        Returns:
            SQLAlchemy: Database instance for ORM operations
        """
        return self.__app_db
    
    @property
    def migration(self) -> Migrate:
        """
        Get the database migration manager.
        
        Returns:
            Migrate: Instance for handling database migrations
        """
        return self.__migration

    @property
    def socket(self) -> SocketIO:
        """
        Get the SocketIO instance for WebSocket operations.
        
        Returns:
            SocketIO: Instance for handling real-time communications
        """
        return self.__socket
    
    @property
    def mail(self) -> Mail:
        """
        Get the Flask-Mail instance for email operations.
        
        Returns:
            Mail: Instance for handling email operations
        """
        return self.__mail

    def create_blueprint(self, name: str, **kwargs) -> Blueprint:
        """
        Creates and registers a new Flask Blueprint.
        
        Args:
            name: Name of the blueprint
            **kwargs: Additional blueprint configuration options
                     Supports all Flask Blueprint parameters
        
        Returns:
            Blueprint: The created Flask Blueprint instance
        """
        blueprint = Blueprint(name, self.__name, **kwargs)
        self.__blueprints.append((blueprint, kwargs))
        return blueprint
    
    def __register_all_blueprints(self) -> None:
        """
        Registers all created blueprints with the application.
        Internal method called during application startup.
        """
        for blueprint, kwargs in self.__blueprints:
            super().register_blueprint(blueprint, **kwargs)

    def __import_moduls(self) -> None:
        """
        Imports modules from the configured routes and sockets directories.
        Internal method called during application startup.
        """
        from integral_flask_project.import_moduls import import_moduls
        if path.exists(self.__path_routes):
            import_moduls(self.__path_routes)
        if path.exists(self.__path_sockets):
            import_moduls(self.__path_sockets)

    def  run(self, host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        load_dotenv: bool = True,
        **kwargs:Any) -> None:
        """
        Initializes and runs the application with the configured settings.
        
        Args:
            **kwargs: Configuration options for Flask's run method
        """
        self.__app_config._init_cors()
        self.__import_moduls()
        self.__register_all_blueprints()
        self.__database.setup() 
        
        match self.__run_type:
            case Integral_flask_project.RUN_TYPE.FLASK:
                super().run(**kwargs)
            case Integral_flask_project.RUN_TYPE.SOKET_IO:
                self.__socket.run(self, **kwargs)