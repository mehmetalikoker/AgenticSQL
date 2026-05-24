import os
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv
from langchain_core.runnables.history import RunnableWithMessageHistory

from managers.agent_manager import AgentManager
from managers.database_manager import DatabaseManager
from managers.session_manager import SessionManager
from managers.ui_manager import UIManager

load_dotenv()


def main() -> None:
    AgentManager.setup_page()
    SessionManager.ensure_state()

    databases = DatabaseManager.get_available_databases()
    active_db_path = UIManager.render_sidebar(databases)

    selected_model = st.session_state.get("selected_model", AgentManager.MODEL_NAME)
    agent_executor, db_engine = AgentManager.init_agent(active_db_path, selected_model)

    UIManager.render_status_panel(active_db_path, db_engine)

    if agent_executor is None or db_engine is None:
        st.error("Agent başlatılamadı. Geçerli bir veritabanı dosyası seçtiğinizden emin olun.")
        return

    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        SessionManager.get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    UIManager.render_chat_interface(agent_with_chat_history, active_db_path)
    st.markdown("---")
    st.caption("🌿 © 2026 AgenticSQL — Yapay Zeka Destekli SQL Arayüzü")


get_available_databases = DatabaseManager.get_available_databases
init_agent = AgentManager.init_agent
get_session_history = SessionManager.get_history


if __name__ == "__main__":
    main()
