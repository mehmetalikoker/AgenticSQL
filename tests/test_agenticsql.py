import pytest
import os
from unittest.mock import MagicMock, patch
from langchain_community.utilities import SQLDatabase
from agenticsql import init_agent

TEST_DB_PATH = "Database/Chinook_Sqlite.sqlite"

@pytest.fixture
def mock_db_engine():
    db = MagicMock(spec=SQLDatabase)
    db.get_usable_table_names.return_value = ["Artist", "Album", "Track"]
    return db


@pytest.fixture
def agent_setup():
    """Create Agent Procces test"""
    if not os.path.exists(TEST_DB_PATH):
        pytest.skip("Test veritabanı bulunamadı, test atlanıyor.")
    return init_agent(TEST_DB_PATH)


# UNIT TESTS
class TestAgenticSQL:

    def test_init_agent_success(self, agent_setup):
        """Scenario: The agent must be successfully installed via a valid DB path."""
        agent, db = agent_setup
        assert agent is not None
        assert db is not None
        assert hasattr(agent, "invoke")

    def test_init_agent_invalid_path(self):
        """Scenario: When an invalid path is given, the system should return None without giving an error."""
        agent, db = init_agent("Database/non_existent.sqlite")
        assert agent is None
        assert db is None

    def test_db_schema_loading(self, agent_setup):
        """Scenario: Database tables must be readable."""
        _, db = agent_setup
        tables = db.get_usable_table_names()
        assert isinstance(tables, list)
        assert len(tables) > 0


    def test_session_history_logic(self):
        """Scenario: Is the chat history object being created correctly?"""
        from langchain_community.chat_message_histories import ChatMessageHistory
        store = {}
        session_id = "test_session"

        if session_id not in store:
            store[session_id] = ChatMessageHistory()

        store[session_id].add_user_message("Merhaba")
        assert len(store[session_id].messages) == 1
        assert store[session_id].messages[0].content == "Merhaba"


# INTEGRATION TEST
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="API Key tanımlı değil")
def test_real_agent_invocation(agent_setup):
    agent, _ = agent_setup
    config = {"configurable": {"session_id": "test_integration"}}
    response = agent.invoke({"input": "Mevcut tabloları listele."}, config=config)

    assert "output" in response
    assert isinstance(response["output"], str)