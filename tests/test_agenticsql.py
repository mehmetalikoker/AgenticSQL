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


class TestDatabaseManager:

    def test_get_available_databases_returns_list(self, tmp_path, monkeypatch):
        """Scenario: get_available_databases geçerli dosyaları liste olarak döndürmeli."""
        db_dir = tmp_path / "Database"
        db_dir.mkdir()
        (db_dir / "test1.sqlite").touch()
        (db_dir / "test2.db").touch()
        (db_dir / "readme.txt").touch()

        monkeypatch.chdir(tmp_path)
        from agenticsql import get_available_databases
        result = get_available_databases()

        assert isinstance(result, list)
        assert "test1.sqlite" in result
        assert "test2.db" in result
        assert "readme.txt" not in result

    def test_get_available_databases_empty_folder(self, tmp_path, monkeypatch):
        """Scenario: Database klasörü boşsa boş liste dönmeli."""
        db_dir = tmp_path / "Database"
        db_dir.mkdir()

        monkeypatch.chdir(tmp_path)
        from agenticsql import get_available_databases
        result = get_available_databases()

        assert result == []

    def test_get_available_databases_creates_folder(self, tmp_path, monkeypatch):
        """Scenario: Database klasörü yoksa otomatik oluşturulmalı."""
        monkeypatch.chdir(tmp_path)
        from agenticsql import get_available_databases
        get_available_databases()

        assert (tmp_path / "Database").exists()

    def test_get_available_databases_only_sqlite_and_db(self, tmp_path, monkeypatch):
        """Scenario: Sadece .sqlite ve .db uzantılı dosyalar listelenmeli."""
        db_dir = tmp_path / "Database"
        db_dir.mkdir()
        (db_dir / "valid.sqlite").touch()
        (db_dir / "valid.db").touch()
        (db_dir / "ignore.csv").touch()
        (db_dir / "ignore.json").touch()

        monkeypatch.chdir(tmp_path)
        from agenticsql import get_available_databases
        result = get_available_databases()

        assert len(result) == 2


class TestSessionHistory:

    def test_new_session_creates_history(self):
        """Scenario: Yeni bir session_id için ChatMessageHistory nesnesi oluşturulmalı."""
        from langchain_community.chat_message_histories import ChatMessageHistory
        store = {}

        def get_session_history(session_id):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        history = get_session_history("session_abc")
        assert isinstance(history, ChatMessageHistory)
        assert len(history.messages) == 0

    def test_same_session_returns_same_history(self):
        """Scenario: Aynı session_id tekrar çağrıldığında aynı nesne dönmeli."""
        from langchain_community.chat_message_histories import ChatMessageHistory
        store = {}

        def get_session_history(session_id):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        history1 = get_session_history("session_xyz")
        history1.add_user_message("İlk mesaj")
        history2 = get_session_history("session_xyz")

        assert history1 is history2
        assert len(history2.messages) == 1

    def test_different_sessions_are_isolated(self):
        """Scenario: Farklı session'lar birbirinden bağımsız olmalı."""
        from langchain_community.chat_message_histories import ChatMessageHistory
        store = {}

        def get_session_history(session_id):
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        get_session_history("session_A").add_user_message("Mesaj A")
        get_session_history("session_B").add_user_message("Mesaj B1")
        get_session_history("session_B").add_user_message("Mesaj B2")

        assert len(store["session_A"].messages) == 1
        assert len(store["session_B"].messages) == 2

    def test_message_order_preserved(self):
        """Scenario: Mesajlar eklenme sırasına göre korunmalı."""
        from langchain_community.chat_message_histories import ChatMessageHistory
        history = ChatMessageHistory()
        history.add_user_message("Birinci")
        history.add_ai_message("Cevap")
        history.add_user_message("İkinci")

        assert history.messages[0].content == "Birinci"
        assert history.messages[1].content == "Cevap"
        assert history.messages[2].content == "İkinci"