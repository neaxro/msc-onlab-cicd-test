from flask import Flask
from flask_restful import Api
import pytest

from app.utils.time_management import utcnow

@pytest.fixture()
def app():
    app = Flask(__name__)
    api = Api(app)
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# --------------------------------------------
# |                 TESTS                    |
# --------------------------------------------

def test_dummy_1(client):
    sum = 1 + 1
    assert sum == 2

def test_dummy_2(client):
    sum = 1 + 2
    assert sum > 2

def test_json_validation(client):
    
    date = utcnow()
    assert date is not None
