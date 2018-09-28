def test_login_get_method(client):
    response = client.get('/api/login', follow_redirects=True)
    # assert b'Hello, World!' in response.data
    assert not response.status_code < 400  # Should be 405, in case we want to narrow it down


def test_unauthorized_access(client):
    response = client.get('/content/', follow_redirects=False)
    # import ipdb
    # ipdb.set_trace()
    # FIXME: this is not working properly
    assert response.status_code < 300


# def test_unauthorized_password_change(client):
#     # import ipdb
#     # ipdb.set_trace()
#     response = client.get('/settings/profile')
#     assert not response.status_code < 300
