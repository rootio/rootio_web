# Testing rootio-web

## Configuration
Add the following to `rootio/config.py`:

```python
class TestConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://' # store db in memory

    MAIL_DEFAULT_SENDER = 'test@example.com'
```

## Running the test suite
```shell
python -m tests
```
