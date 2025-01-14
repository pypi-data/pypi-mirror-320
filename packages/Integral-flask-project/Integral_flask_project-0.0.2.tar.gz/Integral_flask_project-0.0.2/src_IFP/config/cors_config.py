from typing import Dict, Generator, List
from flask import Flask
from flask_cors import CORS
from functools import lru_cache

from src_IFP.config.cors.cors import CORS_config


class CORS_manager:
    """
    Manages CORS configurations for Flask applications.
    Allows creating and managing multiple CORS configurations for different blueprints.

    Attributes:
        __app (Flask): The Flask application instance.
        __configs (Dict[str, CORS_config]): Dictionary storing CORS configurations.
    """

    def __init__(self, app: Flask) -> None:
        """
        Initialize the CORS manager.

        Args:
            app (Flask): The Flask application instance to manage CORS for.
        """
        self.__app = app
        self.__configs: Dict[str, CORS_config] = {}
        self.__cors_applied = False  # Track if CORS has already been applied

    @property
    def configs(self) -> Dict[str, CORS_config]:
        """
        Get all CORS configurations.

        Returns:
            Dict[str, CORS_config]: Dictionary of CORS configurations keyed by name.
        """
        return self.__configs

    def create_config(self, name: str, **kwargs) -> None:
        """
        Create a new CORS configuration.

        Args:
            name (str): Name of the configuration.
            **kwargs: Other CORS configuration options.

        Raises:
            ValueError: If the 'name' parameter is not provided or is a duplicate.
        """
        if not name:
            raise ValueError(f"A CORS configuration needs to have a name")
        if name in self.__configs:
            raise ValueError(f"A CORS configuration with the name '{name}' already exists.")

        self.__configs[name] = CORS_config(name=name, **kwargs)

    @lru_cache(maxsize=128)
    def _get_endpoints(self)->Generator:
        """
        Get all registered endpoints in the Flask app, including both global and blueprint routes.

        Returns:
            List[str]: List of all endpoint URLs.
        """
        for rule in self.__app.url_map.iter_rules():
            yield rule.rule


    def _apply_cors(self) -> None:
        """
        Apply CORS configurations to all registered endpoints.
        Should be called after all routes are registered.
        """
        resources = {}
        for config_name, config in self.__configs.items():
            for route in self._get_endpoints():
                resources[route] = config.to_dict()

        if resources:
            CORS(self.__app, resources=resources)