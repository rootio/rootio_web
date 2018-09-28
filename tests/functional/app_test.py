from rootio import config


def test_create_app(client):
    assert client.application.config['TESTING']

def test_database(client):
    assert client.application.config['SQLALCHEMY_DATABASE_URI'] == config.TestConfig.SQLALCHEMY_DATABASE_URI
