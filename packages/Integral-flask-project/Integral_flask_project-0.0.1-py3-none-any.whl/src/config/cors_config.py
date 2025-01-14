from typing import Dict, List
from flask import Flask
from flask_cors import CORS
from functools import lru_cache

from src_IFP.config.cors.cors import CORS_config

class CORS_manager:
    """
    Manages CORS configurations for Flask applications.
    Allows creating and managing multiple CORS configurations for different blueprints.

    Attributes:
        __app (Flask): The Flask application instance
        __configs (Dict[str, CORS_config]): Dictionary storing CORS configurations
    """

    def __init__(self, app: Flask) -> None:
        """
        Initialize the CORS manager.

        Args:
            app (Flask): The Flask application instance to manage CORS for
        """
        self.__app = app
        self.__configs: Dict[str, CORS_config] = {}

    @property
    def configs(self) -> Dict[str, CORS_config]:
        """
        Get all CORS configurations.

        Returns:
            Dict[str, CORS_config]: Dictionary of CORS configurations keyed by name
        """
        return self.__configs

    def create_config(self, **kwargs) -> None:
        """
        Create a new CORS configuration and set up response headers.

        Args:
            **kwargs: Configuration options including:
                     - name (str): Required. Name of the configuration
                     - Other CORS configuration options

        Raises:
            ValueError: If name parameter is not provided
        """
        name = kwargs.pop("name", None)
        if not name:
            raise ValueError("name parameter is required")
            
        config = CORS_config(name=name, **kwargs)
        self.__configs[name] = config

        @self.__app.after_request
        def add_headers(response):
            """
            Add CORS headers to the response.

            Args:
                response: Flask response object

            Returns:
                Modified response with CORS headers
            """
            for header, value in config.header_values.items():
                if header in config.allow_headers:
                    response.headers[header] = value
            return response

    @lru_cache(maxsize=128)
    def _get_endpoints(self, blueprint_name: str) -> List[str]:
        """
        Get all endpoints for a given blueprint name.
        Results are cached for performance.

        Args:
            blueprint_name (str): Name of the blueprint

        Returns:
            List[str]: List of endpoint URLs for the blueprint
        """
        return [
            rule.rule
            for rule in self.__app.url_map.iter_rules()
            if rule.endpoint.startswith(f"{blueprint_name}.")
        ]

    def _apply_cors(self) -> None:
        """
        Apply CORS configurations to all registered endpoints.
        Should be called after all routes are registered.
        """
        for config_name, config in self.__configs.items():
            resources = {route: config.to_dict() for route in self._get_endpoints(config_name)}
            CORS(self.__app, resources=resources)