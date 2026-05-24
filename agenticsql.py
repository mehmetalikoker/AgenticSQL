from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv

from managers.agent_manager import AgentManager
from managers.database_manager import DatabaseManager
from managers.login_manager import LoginManager
from managers.session_manager import SessionManager
from managers.ui_manager import UIManager

load_dotenv()


def main() -> None:
    AgentManager.setup_page()

    if not LoginManager.is_authenticated():
        LoginManager.render_login_page()
        return

    SessionManager.ensure_state()

    databases = DatabaseManager.get_available_databases()
    active_db_uri, active_db_label = UIManager.render_sidebar(databases)

    selected_model = st.session_state.get("selected_model", AgentManager.MODEL_NAME)
    agent_executor, db_engine = AgentManager.init_agent(active_db_uri, selected_model)

    UIManager.render_status_panel(active_db_label, db_engine)

    if not active_db_uri:
        st.info("Lütfen sol menüden bir veritabanına bağlanın.")
        return

    if agent_executor is None or db_engine is None:
        st.error("Veritabanına bağlanılamadı. Bağlantı bilgilerini kontrol edin.")
        return

    UIManager.render_chat_interface(agent_executor, active_db_label)
    st.markdown("---")
    st.caption("🌿 © 2026 AgenticSQL — Yapay Zeka Destekli SQL Arayüzü")


get_available_databases = DatabaseManager.get_available_databases
init_agent = AgentManager.init_agent


if __name__ == "__main__":
    main()
