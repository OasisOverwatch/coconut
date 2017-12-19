import os


class Config(object):
    """
    Base Config
    """
    ENV = None
    DEBUG = False
    DEFAULT_COMMAND_PREFIX = os.environ.get('DEFAULT_COMMAND_PREFIX', '!')
    DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')
    OASIS_HOSTNAME = os.environ.get('OASIS_HOSTNAME', '')
    OASIS_PORT = int(os.environ.get('OASIS_PORT', 5000))


class ProdConfig(Config):
    ENV = 'prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True
    # Use an in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


def get_config(name=os.getenv('CONFIG', 'dev')):
    assert name, 'A configuration name is required'
    for config in Config.__subclasses__():
        if config.ENV == name:
            return config

    assert False, 'Requested configuration "{}" was not found'.format(name)
