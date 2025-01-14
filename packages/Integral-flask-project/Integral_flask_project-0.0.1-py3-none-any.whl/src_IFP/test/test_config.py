import unittest
from src_IFP.config.config import Config, Development_config, Production_config

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        
        self.assertEqual(config.FLASK_APP, 'app.py')
        self.assertEqual(config.FLASK_NAME, 'My Flask App')

    def test_mail_config(self):
        """Test mail configuration values"""
        config = Config()
        
        self.assertEqual(config.MAIL_SERVER, 'smtp.gmail.com')
        self.assertEqual(config.MAIL_PORT, 587)
        self.assertTrue(config.MAIL_USE_TLS)
        self.assertFalse(config.MAIL_USE_SSL)

    def test_jwt_config(self):
        """Test JWT configuration values"""
        config = Config()
        
        self.assertEqual(config.JWT_ACCESS_TOKEN_EXPIRES, 3600)
        self.assertEqual(config.JWT_REFRESH_TOKEN_EXPIRES, 86400)

    def test_socketio_config(self):
        """Test SocketIO configuration values"""
        config = Config()
        
        self.assertEqual(config.SOCKETIO_PING_TIMEOUT, 5)
        self.assertEqual(config.SOCKETIO_PING_INTERVAL, 25)

class TestDevelopmentConfig(unittest.TestCase):
    def test_development_config(self):
        """Test development configuration values"""
        config = Development_config()
        
        self.assertTrue(config.DEBUG)
        self.assertEqual(config.FLASK_ENV, 'development')
        self.assertTrue('development_database' in config.SQLALCHEMY_DATABASE_URI)

class TestProductionConfig(unittest.TestCase):
    def test_production_config(self):
        """Test production configuration values"""
        config = Production_config()
        
        self.assertFalse(config.DEBUG)
        self.assertEqual(config.FLASK_ENV, 'production')
        self.assertTrue('production_database' in config.SQLALCHEMY_DATABASE_URI)

   

if __name__ == '__main__':
    unittest.main()