from os import urandom, getenv
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """
    Base configuration class for Flask application.
    Loads configuration values from environment variables with defaults.

    Attributes:
        FLASK_APP (str): Main application file
        FLASK_NAME (str): Application name
        SECRET_KEY (str): Secret key for session management
        DEBUG (bool): Debug mode flag
        FLASK_ENV (str): Environment name (development/production)
        
        # Database Configuration
        SQLALCHEMY_DATABASE_URI (str): Database connection URI
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): SQLAlchemy modification tracking
        
        # Email Configuration
        MAIL_SERVER (str): SMTP server address
        MAIL_PORT (int): SMTP server port
        MAIL_USE_TLS (bool): Enable TLS
        MAIL_USE_SSL (bool): Enable SSL
        MAIL_USERNAME (str): Email username
        MAIL_PASSWORD (str): Email password
        MAIL_DEFAULT_SENDER (str): Default sender email
        
        # JWT Configuration
        JWT_SECRET_KEY (str): Secret key for JWT
        JWT_ACCESS_TOKEN_EXPIRES (int): Access token expiration time
        JWT_REFRESH_TOKEN_EXPIRES (int): Refresh token expiration time
        
        # SocketIO Configuration
        SOCKETIO_MESSAGE_QUEUE (str): Message queue URI
        SOCKETIO_CHANNEL (str): SocketIO channel name
        SOCKETIO_PING_TIMEOUT (int): Ping timeout in seconds
        SOCKETIO_PING_INTERVAL (int): Ping interval in seconds
    """
    
    # General Flask Config
    FLASK_APP = getenv('FLASK_APP', 'app.py')
    FLASK_NAME = getenv('FLASK_NAME', 'My Flask App')
    SECRET_KEY = getenv('SECRET_KEY', urandom(24).hex())
    DEBUG = getenv('DEBUG', 'False') == 'True'
    FLASK_ENV = getenv('FLASK_ENV', 'development')

    # SQLAlchemy Config
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'

    # Flask-Mail Config
    MAIL_SERVER = getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = getenv('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = getenv('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD', 'your_password')
    MAIL_DEFAULT_SENDER = getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Flask-JWT-Extended Config
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = int(getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # In seconds
    JWT_REFRESH_TOKEN_EXPIRES = int(getenv('JWT_REFRESH_TOKEN_EXPIRES', 86400))  # In seconds (1 day)

    # Flask-SocketIO Config
    SOCKETIO_MESSAGE_QUEUE = getenv('SOCKETIO_MESSAGE_QUEUE', 'redis://localhost:6379/0')
    SOCKETIO_CHANNEL = getenv('SOCKETIO_CHANNEL', 'flask-socketio')
    SOCKETIO_PING_TIMEOUT = int(getenv('SOCKETIO_PING_TIMEOUT', 5))
    SOCKETIO_PING_INTERVAL = int(getenv('SOCKETIO_PING_INTERVAL', 25))


class Development_config(Config):
    """
    Development environment configuration.
    Inherits from base Config class and overrides specific settings.

    Attributes:
        DEBUG (bool): Enable debug mode
        FLASK_ENV (str): Set to 'development'
        SQLALCHEMY_DATABASE_URI (str): Development database URI
    """
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI_DEV', 'sqlite:///development_database.sql')


class Production_config(Config):
    """
    Production environment configuration.
    Inherits from base Config class and overrides specific settings.

    Attributes:
        DEBUG (bool): Disable debug mode
        FLASK_ENV (str): Set to 'production'
        SQLALCHEMY_DATABASE_URI (str): Production database URI
    """
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI_PROD', 'sqlite:///production_database.sql')