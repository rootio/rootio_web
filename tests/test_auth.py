import pytest

@pytest.fixture
def app():
    from rootio import create_app
    from rootio.config import TestConfig
    app = create_app(TestConfig)
    return app

@pytest.fixture
def db(app):
    from rootio.extensions import db
    with app.app_context():
        db.create_all()
        try:
            yield db
        finally:
            db.drop_all()

def test_permissions(db):
    from rootio.user import User, RootioUser
    from rootio.user.constants import ADMIN, NETWORK_ADMIN, NETWORK_USER, ACTIVE
    from rootio.user import auth
    from rootio.radio.models import Network, Station

    def user_fixture(name, role_code):
        user = User(
            name=name,
            email=name + u'@example.com',
            password=u'123456',
            role_code=role_code,
            status_code=ACTIVE,
        )
        db.session.add(user)
        return user

    admin = user_fixture(u'admin', ADMIN)
    net_admin_1 = user_fixture(u'net_admin_1', NETWORK_ADMIN)
    net_admin_2 = user_fixture(u'net_admin_2', NETWORK_ADMIN)
    demo = user_fixture(u'demo', NETWORK_USER)
    db.session.flush()

    network_1 = Network(
        name="test network 1",
        networkusers=[RootioUser.query.get(net_admin_1.id)],
    )
    db.session.add(network_1)

    network_2 = Network(
        name="test network 2",
        networkusers=[RootioUser.query.get(net_admin_2.id)],
    )
    db.session.add(network_2)

    station_1 = Station(
        name="test station 1",
        about="This is a station used only for test purposes",
        frequency='103.8',
        network=network_1,
        timezone='Africa/Abidjan',
        owner=admin,
        client_update_frequency=30,
        analytic_update_frequency=30,
        broadcast_ip='230.255.255.257',
        outgoing_gateways=[],
        api_key='TESTAPIKEY',
    )
    db.session.add(station_1)
    db.session.flush()

    assert auth.can_edit_network(network_1, admin)
    assert auth.can_edit_network(network_1, net_admin_1)
    assert not auth.can_edit_network(network_1, net_admin_2)
    assert not auth.can_edit_network(network_1, demo)

    assert auth.can_edit_network(network_2, admin)
    assert auth.can_edit_network(network_2, net_admin_2)
    assert not auth.can_edit_network(network_2, net_admin_1)
    assert not auth.can_edit_network(network_2, demo)

    assert auth.can_edit_station(station_1, admin)
    assert auth.can_edit_station(station_1, net_admin_1)
    assert not auth.can_edit_station(station_1, net_admin_2)
    assert not auth.can_edit_station(station_1, demo)
