import os
from typing import Any, Dict, List, Optional

import streamlit as st
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.utilities import SQLDatabase

from managers.database_manager import DatabaseManager
from managers.session_manager import SessionManager


class UIManager:
    @staticmethod
    def render_sidebar(databases: List[str]) -> Optional[str]:
        with st.sidebar:
            st.title("📟 AgenticSQL")
            st.markdown("---")

            if not databases:
                st.error("Lütfen 'Database' klasörüne bir .sqlite dosyası ekleyin.")
                st.stop()

            selected_db_file = st.selectbox("Veritabanı Seçin", options=databases, index=0)
            selected_path = DatabaseManager.build_path(selected_db_file)

            if st.session_state.get("active_db") != selected_path:
                st.session_state.active_db = selected_path
                SessionManager.reset_chat()

            return selected_path

    @staticmethod
    def render_status_panel(db_path: str, db_engine: Optional[SQLDatabase]) -> None:
        with st.sidebar:
            st.subheader("📊 Sistem Durumu")
            st.success(f"Aktif: `{os.path.basename(db_path)}`")
            st.subheader("🗂️ Tablo Listesi")

            if db_engine is None:
                st.caption("Veritabanı bağlanamadı.")
            else:
                try:
                    tables = db_engine.get_usable_table_names()
                    for table in tables:
                        st.markdown(f"- `{table}`")
                except Exception:
                    st.caption("Tablolar okunurken hata oluştu.")

            st.markdown("---")
            if st.button("Sohbeti Sıfırla"):
                SessionManager.reset_chat()

    @staticmethod
    def render_chat_interface(agent_with_chat_history: RunnableWithMessageHistory, db_path: str) -> None:
        st.title("🤖 SQL Agent: Enterprise Data Interface")
        st.caption(f"Su anda `{os.path.basename(db_path)}` üzerinde çalışıyorsunuz.")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_prompt = st.chat_input("Veritabanına bir soru sor...")
        if not user_prompt:
            return

        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Veri ambarı taranıyor..."):
                try:
                    session_id = f"session_{os.path.basename(db_path)}"
                    config: Dict[str, Any] = {"configurable": {"session_id": session_id}}
                    response = agent_with_chat_history.invoke({"input": user_prompt}, config)
                    answer = response["output"]

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as error:
                    st.error(f"Analiz sırasında bir sorun çıktı: {error}")
