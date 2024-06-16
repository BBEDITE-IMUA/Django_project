"""
This module contains the application configuration for the 'main' app.

Django uses this configuration to manage the 'main' app and its interactions with the rest of the project.
"""

from django.apps import AppConfig


class MainConfig(AppConfig):
    """
    Application configuration for the 'main' app.

    Attributes:
        default_auto_field: The default auto field type to use for automatically created primary keys.
        name: The name of the app.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
