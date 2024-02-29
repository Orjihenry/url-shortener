import os
"""
    Copy config_example.py to a new file named config.py.
    Replace placeholder values in config.py with actual configuration values,
    such as database credentials and secret keys.
"""


# {% include 'navbar.html' %}
class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'your database config here'
    SECRET_KEY = 'your_secret_key'


class ProductionConfig(Config):
    # production configs goes here
    pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test secret key'


# Determine the env (development, production, testing)
# You can set an environment variable (e.g., FLASK_ENV) in your shell or in your .env file
# If not set, default to DevelopmentConfig
app_env = os.environ.get('FLASK_ENV', 'development')

if app_env == 'production':
    app_config = ProductionConfig()
elif app_env == 'testing':
    app_config = TestingConfig()
else:
    app_config = DevelopmentConfig()
