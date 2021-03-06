"""Pytest fixtures to be used across multiple tests.
"""

import pytest
from sqlalchemy import text
from flask_migrate import upgrade
from src import create_app
from src.database import db
from src.model import Activity
from seed import seed_game_entries

@pytest.fixture
def app():
    """Fixture to have access to the Flask application object, with
    the database structure already created and tables seeded. Persists
    once per function.
    """
    app = create_app('src.config.TestConfig')

    with app.app_context():
        # Run alembic migrations on the database
        upgrade(directory='migrations')
        
        # Seed initial records to the database for testing:
        game_entries = seed_game_entries()

        for game in game_entries.get('games'):
            activity = Activity(**game)
            db.session.add(activity)
        db.session.commit()
    
    yield app
    # Teardown: Drop all tables Alembic would've created
    with app.app_context():
        db.engine.execute(text('drop table activity, alembic_version, submissions;'))


@pytest.fixture
def client(app):
    """A test client for making API requests"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for CLI commands."""
    return app.test_cli_runner()