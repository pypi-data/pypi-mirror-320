import unittest
from integral_flask_project import Integral_flask_project
from flask_jwt_extended import create_access_token, jwt_required
from flask import json
import os

class TestIntegralFlaskProject(unittest.TestCase):
    def setUp(self):
        """Set up test application"""
        # Configure test environment
        os.environ['FLASK_ENV'] = 'development'
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
        os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Create app instance
        self.app = Integral_flask_project(__name__)
        self.client = self.app.test_client()
        
        # Create test database and context
        with self.app.app_context():
            self.app.db.create_all()
            
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            self.app.db.drop_all()

    def test_basic_route(self):
        """Test basic route creation and response"""
        @self.app.route('/test')
        def test_route():
            return {'message': 'Test successful'}
            
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Test successful')

    def test_blueprint_creation(self):
        """Test blueprint creation and routing"""
        api = self.app.create_blueprint('api', url_prefix='/api')
        
        @api.route('/test')
        def test_route():
            return {'message': 'Blueprint test'}
            
        self.app.register_blueprint(api)
        response = self.client.get('/api/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Blueprint test')

    def test_jwt_authentication(self):
        """Test JWT authentication functionality"""
        @self.app.route('/protected')
        @jwt_required()
        def protected_route():
            return {'message': 'Protected content'}

        # Test without token
        response = self.client.get('/protected')
        self.assertEqual(response.status_code, 401)

        # Test with valid token
        with self.app.app_context():
            access_token = create_access_token(identity='test_user')
            headers = {'Authorization': f'Bearer {access_token}'}
            response = self.client.get('/protected', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['message'], 'Protected content')

    def test_database_operations(self):
        """Test database model creation and operations"""
        class TestModel(self.app.db.Model):
            id = self.app.db.Column(self.app.db.Integer, primary_key=True)
            name = self.app.db.Column(self.app.db.String(80))

        with self.app.app_context():
            # Create tables
            self.app.db.create_all()
            
            # Test model creation
            test_entry = TestModel(name='test_name')
            self.app.db.session.add(test_entry)
            self.app.db.session.commit()
            
            # Test model query
            result = TestModel.query.filter_by(name='test_name').first()
            self.assertIsNotNone(result)
            self.assertEqual(result.name, 'test_name')

    def test_error_handling(self):
        """Test custom error handlers"""
        @self.app.errorhandler(404)
        def not_found(error):
            return {'error': 'Resource not found'}, 404

        response = self.client.get('/non-existent')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Resource not found')

if __name__ == '__main__':
    unittest.main()