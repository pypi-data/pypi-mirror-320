import unittest
from unittest.mock import patch, MagicMock
from integral_flask_project import import_moduls

class TestModuleImporter(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.test_package = "test_package"

    @patch('importlib.import_module')
    @patch('pkgutil.iter_modules')
    def test_import_single_module(self, mock_iter_modules, mock_import_module):
        """Test importing a single module without submodules"""
        # Mock a package with one module
        mock_package = MagicMock()
        mock_package.__path__ = ['/fake/path']
        mock_import_module.return_value = mock_package
        
        # Mock iter_modules to return one module
        mock_iter_modules.return_value = [
            (None, 'module1', False)
        ]

        result = import_moduls(self.test_package)
        
        self.assertEqual(len(result), 1)
        self.assertIn(f"{self.test_package}.module1", result)

    @patch('importlib.import_module')
    @patch('pkgutil.iter_modules')
    def test_import_nested_modules(self, mock_iter_modules, mock_import_module):
        """Test importing nested modules"""
        # Mock package with nested modules
        mock_package = MagicMock()
        mock_package.__path__ = ['/fake/path']
        mock_import_module.return_value = mock_package
        
        # First iteration: root package
        # Second iteration: subpackage
        mock_iter_modules.side_effect = [
            [(None, 'subpackage', True)],
            [(None, 'module1', False)]
        ]

        result = import_moduls(self.test_package)
        
        self.assertEqual(len(result), 2)
        self.assertIn(f"{self.test_package}.subpackage", result)
        self.assertIn(f"{self.test_package}.subpackage.module1", result)

    @patch('importlib.import_module')
    @patch('pkgutil.iter_modules')
    def test_import_empty_package(self, mock_iter_modules, mock_import_module):
        """Test importing an empty package"""
        mock_package = MagicMock()
        mock_package.__path__ = ['/fake/path']
        mock_import_module.return_value = mock_package
        
        # Return empty list of modules
        mock_iter_modules.return_value = []

        result = import_moduls(self.test_package)
        
        self.assertEqual(len(result), 0)

    @patch('importlib.import_module')
    def test_import_invalid_package(self, mock_import_module):
        """Test importing an invalid package"""
        mock_import_module.side_effect = ImportError()

        with self.assertRaises(ImportError):
            import_moduls("invalid_package")

if __name__ == '__main__':
    unittest.main()