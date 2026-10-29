import os
import configparser
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from Database.DataBaseInterface import DataBaseInterface

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

def get_database_url():
    return os.getenv("LAPAGENT_DATABASE_URL") or cfg.get("database", "database_url", fallback=None)
@pytest.fixture
def database_url():
    return get_database_url()
@pytest.mark.database
def test_connection():
    url = get_database_url()
    assert url is not None, "Database URL must be set"

    engine = create_engine(url, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
@pytest.mark.database
def test_interface_initialize():
    url = get_database_url()
    assert url is not None, "Database URL must be set"
    db = DataBaseInterface(url)
    with db.SessionLocal() as session:
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        role_count = result.scalar_one()
        assert role_count >= 3

        result = session.execute(text("SELECT COUNT(*) FROM \"AI_Models\""))
        model_count = result.scalar_one()
        assert model_count >= 1