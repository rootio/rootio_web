def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, authenticated, and role fields are defined correctly
    """
    assert new_user.email == 'rootio@example.org'
    assert new_user.password != 'rootiotest'
    assert new_user.role == 'network user'


def test_setting_password(new_user):
    """
    GIVEN an existing User
    WHEN the password for the user is set
    THEN check the password is stored correctly and not as plaintext
    """
    new_user._set_password('MyNewPassword')
    assert new_user.password != 'MyNewPassword'
    assert new_user.check_password('MyNewPassword')
    assert not new_user.check_password('MyNewPassword2')
    assert not new_user.check_password('FlaskIsAwesome')


