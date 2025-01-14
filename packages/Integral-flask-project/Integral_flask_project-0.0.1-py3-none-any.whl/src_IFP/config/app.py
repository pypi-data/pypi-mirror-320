from typing import Dict, Tuple
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from src_IFP.config.database_config import Database_config

from src_IFP.config.config import Production_config
from src_IFP.config.cors_config import CORS_manager

class App_config:

    _instance = None

    def __new__(cls, app:Flask) -> 'App_config':
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, app:Flask) -> None:
        self.__app:Flask = app
        self._cors:CORS_manager = CORS_manager(app)


    def create_app(self, env:object|str|None) -> Tuple[JWTManager, Tuple[SQLAlchemy, Migrate, Database_config], SocketIO, Mail]:
        self.__init_env(env)
        jwt = self.__init_JWT()
        app_db = self.__init_database()
        socket = self.__init_SocketIO()
        mail = self.__init_mail()
        return jwt, app_db, socket, mail

    def __init_env(self, env:object|str|None)->None:
        if not env: self.__app.config.from_object(Production_config)
        elif env: self.__app.config.from_object(env)

    def _init_cors(self)->None:
        if not self._cors.configs: CORS(self.__app)
        else: self._cors._apply_cors()

    def __init_database(self)->Tuple[SQLAlchemy, Migrate, Database_config]:
        database = Database_config(self.__app)
        return database.app_db, database.migration, database

    def __init_SocketIO(self)->SocketIO:
        return SocketIO(self.__app, message_queue=self.__app.config['SOCKETIO_MESSAGE_QUEUE'])

    def __init_JWT(self)->JWTManager:
        return JWTManager(self.__app)
    
    def __init_mail(self)->Mail:
        return Mail(self.__app)