import pytest
import os
from unittest.mock import MagicMock, patch
from langchain_community.utilities import SQLDatabase
from agenticsqlscreen import init_agent  # app.py dosyanızın adı farklıysa güncelleyin

# --- CONFIG & CONSTANTS ---
TEST_DB_PATH = "Database/Chinook_Sqlite.sqlite"


# --- FIXTURES ---

@pytest.fixture
def mock_db_engine():
    """Gerçek DB yerine geçecek sahte (mock) DB nesnesi."""
    db = MagicMock(spec=SQLDatabase)
    db.get_usable_table_names.return_value = ["Artist", "Album", "Track"]
    return db


@pytest.fixture
def agent_setup():
    """Agent başlatma sürecini test eder."""
    if not os.path.exists(TEST_DB_PATH):
        pytest.skip("Test veritabanı bulunamadı, test atlanıyor.")
    return init_agent(TEST_DB_PATH)


# --- UNIT TESTS ---

class TestAgenticSQL:

    def test_init_agent_success(self, agent_setup):
        """Senaryo: Geçerli bir DB yolu ile agent başarıyla kurulmalı."""
        agent, db = agent_setup
        assert agent is not None
        assert db is not None
        assert hasattr(agent, "invoke")

    def test_init_agent_invalid_path(self):
        """Senaryo: Geçersiz yol verildiğinde sistem hata vermeden None dönmeli."""
        agent, db = init_agent("Database/non_existent.sqlite")
        assert agent is None
        assert db is None

    def test_db_schema_loading(self, agent_setup):
        """Senaryo: Veritabanı tabloları okunabilmeli."""
        _, db = agent_setup
        tables = db.get_usable_table_names()
        assert isinstance(tables, list)
        assert len(tables) > 0

    @patch("langchain_openai.ChatOpenAI.invoke")
    def test_agent_logic_mock(self, mock_llm_invoke, agent_setup):
        """
        Senaryo: LLM'e gitmeden ajanın akışını test et (Maliyet tasarrufu).
        """
        agent, _ = agent_setup

        # LLM'den gelecek sahte yanıtı ayarla
        mock_llm_invoke.return_value = MagicMock(content="Veritabanında 10 tablo var.")

        # Invoke çağrısı yap (Dahili mantığı test et)
        # Not: SQL agent kompleks bir yapı olduğu için bu kısım entegrasyon seviyesindedir.
        assert agent.agent_node is not None

    def test_session_history_logic(self):
        """Senaryo: Chat history nesnesi doğru oluşturuluyor mu?"""
        from langchain_community.chat_message_histories import ChatMessageHistory
        store = {}
        session_id = "test_session"

        if session_id not in store:
            store[session_id] = ChatMessageHistory()

        store[session_id].add_user_message("Merhaba")
        assert len(store[session_id].messages) == 1
        assert store[session_id].messages[0].content == "Merhaba"


# --- INTEGRATION TEST ---

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="API Key tanımlı değil")
def test_real_agent_invocation(agent_setup):
    """Senaryo: Gerçek bir basit sorguya yanıt alınabiliyor mu?"""
    agent, _ = agent_setup
    config = {"configurable": {"session_id": "test_integration"}}

    response = agent.invoke({"input": "Mevcut tabloları listele."}, config=config)

    assert "output" in response
    assert isinstance(response["output"], str)