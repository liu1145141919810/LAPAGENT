import pytest
import pytest_asyncio

import os
import sys
from pathlib import Path
_current_dir = Path(__file__).parent
sys.path.append(str(_current_dir.parent))

from public.logger import setup_logger
logger = setup_logger(__name__)
from Database.DataBaseInterface import DataBaseInterface
from Agent.agent import Agent
from Redis.redis_client import RedisManager

test_db_path = _current_dir / "test.db"
db = DataBaseInterface(test_db_path)
redis_manager = RedisManager()

def clean_test(agent):
    if agent is None:
        return
    for key,value in agent.toolbox.backinfo["test_box"].items():
        agent.toolbox.backinfo["test_box"][key] = None
    agent.reload_messages()

@pytest_asyncio.fixture(scope="session")
async def theAgent():
    agent = Agent(db, redis_manager)
    logger.info("Setting up the agent for testing.")
    yield agent
    if os.path.exists(test_db_path):
       os.remove(test_db_path)
       logger.info("Removed test database.")

@pytest.mark.asyncio
async def test_setup(theAgent):
    assert theAgent is not None

@pytest.mark.asyncio
async def test_memory(theAgent):
    assert theAgent is not None
    try:
        msg = "What's the first sentence of this conversation?"
        result = await theAgent.session_interact(msg)
        assert theAgent.toolbox.backinfo["test_box"]["load_current_history"] is not None
    finally:
        clean_test(theAgent)
     
@pytest.mark.asyncio
async def test_history(theAgent):
    assert theAgent is not None
    try:
        msg = "Remember I am testing the agent."
        result = await theAgent.session_interact(msg)
        assert theAgent.toolbox.backinfo["test_box"]["save_memory"] is not None
        clean_test(theAgent)

        msg = "What am I doing?"
        result = await theAgent.session_interact(msg)
        assert theAgent.toolbox.backinfo["test_box"]["load_memory"] is not None
    finally:
        clean_test(theAgent)

@pytest.mark.asyncio
async def test_search_the_Internet(theAgent):
    assert theAgent is not None
    try:
        msg = "Please search the Internet, just for testing purposes."
        result = await theAgent.session_interact(msg)
        assert theAgent.toolbox.backinfo["test_box"]["search_the_Internet"] is not None
    finally:
        clean_test(theAgent)