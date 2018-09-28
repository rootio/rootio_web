def test_login_get_method(client, station):
    response = client.get('/api/station/1/information')
    # import ipdb
    # ipdb.set_trace()
    assert response == False

