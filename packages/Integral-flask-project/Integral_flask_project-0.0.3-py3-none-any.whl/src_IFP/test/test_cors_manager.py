import unittest
from unittest.mock import patch
from flask import Flask
from integral_flask_project import Integral_flask_project
from src_IFP.config.cors_config import CORS_manager

class TestCORSManager(unittest.TestCase):
    def setUp(self):
        """Set up test cases with a mock Flask app"""
        self.app = Integral_flask_project(__name__)
        self.cors_manager = CORS_manager(self.app)

        @self.app.route("/")
        def home():
            return "Home"

        @self.app.route("/test")
        def test_route():
            return "Test"

    def tearDown(self):
        """Clean up after tests"""
        self.app = None
        self.cors_manager = None

    def test_create_config_without_name(self):
        """Test creating config without name raises ValueError"""
        with self.assertRaises(ValueError):
            self.cors_manager.create_config()

    def test_create_config_with_name(self):
        """Test creating config with name"""
        self.cors_manager.create_config(
            name="test",
            origins=["http://localhost:3000"],
            methods=["GET", "POST"]
        )
        self.assertIn("test", self.cors_manager.configs)

    def test_get_endpoints(self):
        """Test getting endpoints for a blueprint"""
        endpoints = self.cors_manager._get_endpoints()
        self.assertIsInstance(endpoints, list)
        self.assertIn("/test", endpoints)

    @patch('src_IFP.config.cors_config.CORS')
    def test_apply_cors(self, mock_cors):
        """Test applying CORS configurations"""
        self.cors_manager.create_config(
            name="test",
            origins=["http://localhost:3000"]
        )
        self.cors_manager._apply_cors()

        expected_resources = {  '/static/<path:filename>': 
                                                        {'origins': ['http://localhost:3000'], 'methods': ['GET', 'OPTIONS'], 'allow_headers': ['Content-Type'], 'expose_headers': [], 'supports_credentials': False, 'max_age': 1800.0, 'vary_header': True, 'automatic_options': True, 'send_wildcard': False, 'always_send': True}, 
                                '/': 
                                                        {'origins': ['http://localhost:3000'], 'methods': ['GET', 'OPTIONS'], 'allow_headers': ['Content-Type'], 'expose_headers': [], 'supports_credentials': False, 'max_age': 1800.0, 'vary_header': True, 'automatic_options': True, 'send_wildcard': False, 'always_send': True}, 
                                '/test': 
                                                        {'origins': ['http://localhost:3000'], 'methods': ['GET', 'OPTIONS'], 'allow_headers': ['Content-Type'], 'expose_headers': [], 'supports_credentials': False, 'max_age': 1800.0, 'vary_header': True, 'automatic_options': True, 'send_wildcard': False, 'always_send': True}}
        mock_cors.assert_called_once_with(self.app, resources=expected_resources)

    def test_headers_added_to_response(self):
        """Test CORS headers are added to response"""
        self.cors_manager.create_config(
            name="test",
            origins=["http://localhost:3000"]
        )
        self.cors_manager._apply_cors()

        with self.app.test_client() as client:
            response = client.get("/")
            self.assertIn("Access-Control-Allow-Origin", response.headers)
            self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")

    def test_multiple_configs(self):
        """Test handling of multiple CORS configurations"""
        self.cors_manager.create_config(
            name="test",
            origins=["http://localhost:3000"]
        )
        self.cors_manager.create_config(
            name="admin",
            origins=["https://admin.example.com"]
        )
        self.cors_manager._apply_cors()

        with self.app.test_client() as client:
            response = client.get("/")
            self.assertIn("Access-Control-Allow-Origin", response.headers)
            self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")

if __name__ == '__main__':
    unittest.main()
