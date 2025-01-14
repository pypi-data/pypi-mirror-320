from os import getcwd, path
from flask import Flask
from flask_migrate import Migrate, migrate, upgrade, init, stamp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from contextlib import contextmanager
from src_IFP.config.config import Config

class Database_config(Config):
    MIGRATIONS_PATH = 'database/migrations'

    def __init__(self, app: Flask) -> None:
        super().__init__()
        self.__app: Flask = app
        self.__app_db: SQLAlchemy = SQLAlchemy(app)
        self.__migration = Migrate(app, self.__app_db, directory=self.MIGRATIONS_PATH)

    @property
    def app_db(self) -> SQLAlchemy: 
        return self.__app_db

    @property
    def migration(self) -> Migrate: 
        return self.__migration

    @contextmanager
    def __error_handling(self, operation: str):
        """Contexto para manejar errores de manera consistente"""
        try:
            yield
        except Exception as e:
            print(f"Error durante {operation}: {str(e)}")
            raise RuntimeError(f"Error en {operation}: {str(e)}") from e

    def __validate_uri(self, uri: str) -> None:
        """Valida el URI de la base de datos"""
        if not isinstance(uri, str):
            raise ValueError('Database URI debe ser string')
        if not uri:
            raise ValueError('Database URI no puede estar vacío')

    def __ensure_database_exists(self, uri: str) -> bool:
        """Asegura que la base de datos existe, la crea si es necesario"""
        if not database_exists(uri):
            print("La base de datos no existe. Creándola...")
            with self.__error_handling("creación de base de datos"):
                create_database(uri)
            print("Base de datos creada exitosamente")
            return True
        print("La base de datos ya existe")
        return False

    def __initialize_migrations(self, migrations_dir: str) -> None:
        """Inicializa las migraciones si no existen"""
        if not path.exists(migrations_dir):
            print("Migraciones no inicializadas. Ejecutando `init`...")
            with self.__error_handling("inicialización de migraciones"):
                init()
                migrate()
                stamp()
            print("Migraciones inicializadas exitosamente")
        else:
            print("Las migraciones ya están inicializadas")

    def __apply_pending_migrations(self) -> None:
        """Aplica las migraciones pendientes"""
        print("Verificando y aplicando migraciones pendientes...")
        with self.__error_handling("aplicación de migraciones"):
            upgrade()
        print("Migraciones aplicadas exitosamente")

    def setup(self):
        """Configura la base de datos y las migraciones en producción"""
        uri = self.__app.config.get('SQLALCHEMY_DATABASE_URI')
        if not uri: raise ValueError('SQLALCHEMY_DATABASE_URI is not defined')
        self.__validate_uri(uri)

        if Config.FLASK_ENV != 'production':
            print("Saltando configuración de BD: no estamos en producción")
            return

        # Asegura que la base de datos existe
        is_new_database = self.__ensure_database_exists(uri)

        with self.__app.app_context():
            migrations_dir = path.join(getcwd(), self.__migration.directory)
            
            # Inicializa migraciones si es necesario
            self.__initialize_migrations(migrations_dir)

            # Si es una base de datos nueva, marca las migraciones como aplicadas
            if is_new_database:
                print("Nueva base de datos detectada, marcando migraciones...")
                with self.__error_handling("marcado de migraciones"):
                    stamp()
            
            # Aplica migraciones pendientes
            self.__apply_pending_migrations()

        print("Configuración de base de datos completada exitosamente")