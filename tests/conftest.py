import pytest
from flask import Flask

from flask_hintful import FlaskHintful


@pytest.fixture
def api():
    app = Flask(__name__)
    return FlaskHintful(app)
