from tilt.options import Options


def test_getting_apikey_from_env(monkeypatch):
    apikey = 'fakeapikey'
    monkeypatch.setenv('TILT_API_KEY', apikey)
    opt = Options(None)

    assert opt.apikey == apikey
