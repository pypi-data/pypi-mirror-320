import unittest
from unittest.mock import Mock, patch
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from src_IFP.config.database_config import Database_config
from src_IFP.config.config import Production_config
from src_IFP.config.cors_config import CORS_manager
from src_IFP.config.app import App_config

class TestAppConfig(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app_config = App_config(self.app)

    def tearDown(self):
        """Clean up after each test method."""
        App_config._instance = None

    def test_singleton_pattern(self):
        """Test that App_config follows the singleton pattern."""
        # Create multiple instances
        app1 = Flask('app1')
        app2 = Flask('app2')
        
        config1 = App_config(app1)
        config2 = App_config(app2)
        
        # Verify they're the same instance
        self.assertIs(config1, config2)
        self.assertEqual(id(config1), id(config2))

    @patch('src_IFP.config.app_config.CORS')
    def test_cors_initialization_without_configs(self, mock_cors):
        """Test CORS initialization when no configs are present."""
        # Setup mock
        mock_cors_manager = Mock()
        mock_cors_manager.configs = {}
        self.app_config._cors = mock_cors_manager
        
        # Test initialization
        self.app_config._init_cors()
        
        # Verify CORS was initialized with default settings
        mock_cors.assert_called_once_with(self.app)

    @patch('src_IFP.config.app_config.CORS')
    def test_cors_initialization_with_configs(self, mock_cors):
        """Test CORS initialization when configs are present."""
        # Setup mock
        mock_cors_manager = Mock()
        mock_cors_manager.configs = {'test': {}}
        self.app_config._cors = mock_cors_manager
        
        # Test initialization
        self.app_config._init_cors()
        
        # Verify custom CORS configuration was applied
        mock_cors_manager._apply_cors.assert_called_once()

    def test_env_initialization_with_production_config(self):
        """Test environment initialization with production config."""
        self.app_config._App_config__init_env(None)
        
        # Verify production config was applied
        self.assertEqual(
            self.app.config['ENV'],
            Production_config.ENV
        )

    def test_env_initialization_with_custom_config(self):
        """Test environment initialization with custom config."""
        class CustomConfig:
            ENV = 'custom'
            DEBUG = True
        
        self.app_config._App_config__init_env(CustomConfig)
        
        # Verify custom config was applied
        self.assertEqual(self.app.config['ENV'], 'custom')
        self.assertTrue(self.app.config['DEBUG'])

    @patch('src_IFP.config.app_config.Database_config')
    def test_database_initialization(self, mock_db_config):
        """Test database initialization."""
        # Setup mocks
        mock_db = Mock(spec=SQLAlchemy)
        mock_migrate = Mock(spec=Migrate)
        mock_db_config.return_value = Mock(
            app_db=mock_db,
            migration=mock_migrate,
            spec=Database_config
        )
        
        # Test initialization
        db, migrate, config = self.app_config._App_config__init_database()
        
        # Verify database components were initialized
        self.assertIsInstance(db, Mock)
        self.assertIsInstance(migrate, Mock)
        mock_db_config.assert_called_once_with(self.app)

    @patch('src_IFP.config.app_config.SocketIO')
    def test_socketio_initialization(self, mock_socketio):
        """Test SocketIO initialization."""
        # Setup config
        self.app.config['SOCKETIO_MESSAGE_QUEUE'] = 'redis://localhost:6379/0'
        
        # Test initialization
        socket = self.app_config._App_config__init_SocketIO()
        
        # Verify SocketIO was initialized with correct parameters
        mock_socketio.assert_called_once_with(
            self.app,
            message_queue='redis://localhost:6379/0'
        )

    @patch('src_IFP.config.app_config.JWTManager')
    def test_jwt_initialization(self, mock_jwt):
        """Test JWT initialization."""
        jwt = self.app_config._App_config__init_JWT()
        
        # Verify JWT was initialized
        mock_jwt.assert_called_once_with(self.app)

    @patch('src_IFP.config.app_config.Mail')
    def test_mail_initialization(self, mock_mail):
        """Test mail initialization."""
        mail = self.app_config._App_config__init_mail()
        
        # Verify Mail was initialized
        mock_mail.assert_called_once_with(self.app)

    @patch.multiple('src_IFP.config.app_config',
                   JWTManager=DEFAULT,
                   Database_config=DEFAULT,
                   SocketIO=DEFAULT,
                   Mail=DEFAULT)
    def test_create_app(self, JWTManager, Database_config, SocketIO, Mail):
        """Test complete app creation process."""
        # Setup mocks
        mock_jwt = Mock(spec=JWTManager)
        mock_db = Mock(spec=SQLAlchemy)
        mock_migrate = Mock(spec=Migrate)
        mock_socket = Mock(spec=SocketIO)
        mock_mail = Mock(spec=Mail)
        
        JWTManager.return_value = mock_jwt
        Database_config.return_value = Mock(
            app_db=mock_db,
            migration=mock_migrate
        )
        SocketIO.return_value = mock_socket
        Mail.return_value = mock_mail
        
        # Test app creation
        jwt, (db, migrate, db_config), socket, mail = self.app_config.create_app(Production_config)
        
        # Verify all components were initialized
        self.assertIsInstance(jwt, Mock)
        self.assertIsInstance(db, Mock)
        self.assertIsInstance(migrate, Mock)
        self.assertIsInstance(socket, Mock)
        self.assertIsInstance(mail, Mock)

    def test_error_handling(self):
        """Test error handling during initialization."""
        # Test with invalid environment configuration
        with self.assertRaises(Exception):
            self.app_config.create_app("invalid_config")
        
        # Test with invalid database URI
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'invalid://uri'
        with self.assertRaises(Exception):
            self.app_config._App_config__init_database()

class TestAppConfigIntegration(unittest.TestCase):
    """Integration tests for App_config."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.app = Flask(__name__)
        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test_key',
            'JWT_SECRET_KEY': 'jwt_test_key',
            'SOCKETIO_MESSAGE_QUEUE': 'redis://localhost:6379/0',
            'MAIL_SERVER': 'smtp.test.com',
            'MAIL_PORT': 587,
            'MAIL_USE_TLS': True,
            'MAIL_USERNAME': 'test@test.com',
            'MAIL_PASSWORD': 'test_password'
        })
        self.app_config = App_config(self.app)

    def test_full_app_initialization(self):
        """Test full application initialization with all components."""
        try:
            jwt, (db, migrate, db_config), socket, mail = self.app_config.create_app(None)
            
            # Verify all components are initialized properly
            self.assertIsInstance(jwt, JWTManager)
            self.assertIsInstance(db, SQLAlchemy)
            self.assertIsInstance(migrate, Migrate)
            self.assertIsInstance(socket, SocketIO)
            self.assertIsInstance(mail, Mail)
            
            # Test database operations
            with self.app.app_context():
                db.create_all()
                db.drop_all()
                
        except Exception as e:
            self.fail(f"Full app initialization failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()