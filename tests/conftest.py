import pytest
from rootio.app import create_app
from rootio.user.models import User, UserDetail, NETWORK_USER, ACTIVE
from rootio.radio.models import Station
from rootio.config import TestConfig
from rootio.extensions import db


@pytest.fixture(scope='module')
def new_user():
    # user = RootioUser('rootio@example.org', 'rootiotest')
    user = User(
        name=u'demo',
        email=u'rootio@example.org',
        password=u'rotiotest',
        role_code=NETWORK_USER,
        status_code=ACTIVE,
        user_detail=UserDetail(
            age=10,
            url=u'http://demo.example.com',
            location=u'Hangzhou',
            bio=u'admin Guy is ... hmm ... just a demo guy.'))
    return user


@pytest.fixture
def station():
    return Station(
        id=1,
        name='Test station',
    )


@pytest.fixture
def client(request):
    rootio_app = create_app(config=TestConfig)

    with rootio_app.app_context():
        # alternative pattern to app.app_context().push()
        # all commands indented under 'with' are run in the app context
        db.create_all()
        yield rootio_app.test_client()
        db.session.remove()
        db.drop_all()


# @pytest.fixture(scope='module')
# def init_database():
#     # Create the database and the database table
#     db.create_all()
#
#     # Insert user data
#     user1 = User(email='patkennedy79@gmail.com', plaintext_password='FlaskIsAwesome')
#     user2 = User(email='kennedyfamilyrecipes@gmail.com', plaintext_password='PaSsWoRd')
#     db.session.add(user1)
#     db.session.add(user2)
#     station1 = Station( id=1, name='Test station', )
#     db.session.add(station1)
#
#     # Commit the changes for the users
#     db.session.commit()
#
#    yield db  # this is where the testing happens!
#
#    db.drop_all()
