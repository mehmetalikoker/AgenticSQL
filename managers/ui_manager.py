import os
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage

from managers.agent_manager import AgentManager
from managers.database_manager import DatabaseManager
from managers.session_manager import SessionManager


class UIManager:
    @staticmethod
    def render_sidebar(databases: List[str]) -> Tuple[str, str]:
        """Returns (db_uri, db_label)"""
        with st.sidebar:
            st.markdown(
                "<h1 style='color:#15803d; letter-spacing:1px; font-size:1.6rem;'>🌿 AgenticSQL</h1>",
                unsafe_allow_html=True,
            )
            st.markdown("---")

            db_type = st.radio(
                "Veritabanı Tipi",
                options=["SQLite", "Oracle"],
                horizontal=True,
            )

            db_uri = ""
            db_label = ""

            if db_type == "SQLite":
                if not databases:
                    st.error("Lütfen 'Database' klasörüne bir .sqlite dosyası ekleyin.")
                    st.stop()

                selected_file = st.selectbox("Veritabanı Seçin", options=databases, index=0)
                db_uri = DatabaseManager.build_sqlite_uri(selected_file)
                db_label = selected_file

            else:
                connections = DatabaseManager.load_oracle_connections()
                conn_names = [c["name"] for c in connections]

                action = st.radio(
                    "İşlem",
                    ["Kayıtlı Bağlantı", "Yeni Bağlantı Ekle"],
                    horizontal=True,
                    key="oracle_action",
                )

                if action == "Kayıtlı Bağlantı":
                    if not connections:
                        st.info("Henüz kayıtlı bağlantı yok. 'Yeni Bağlantı Ekle' seçin.")
                    else:
                        selected_name = st.selectbox("Bağlantı Seçin", options=conn_names)
                        selected_conn = next(c for c in connections if c["name"] == selected_name)

                        col1, col2 = st.columns(2)
                        with col1:
                            connect_clicked = st.button("🔌 Bağlan", use_container_width=True)
                        with col2:
                            delete_clicked = st.button("🗑️ Sil", use_container_width=True)

                        if delete_clicked:
                            DatabaseManager.delete_oracle_connection(selected_name)
                            if st.session_state.get("oracle_label") == f"{selected_conn['host']}/{selected_conn['service']}":
                                st.session_state.oracle_uri = ""
                                st.session_state.oracle_label = ""
                                SessionManager.reset_chat()
                            st.rerun()

                        if connect_clicked:
                            st.session_state.oracle_uri = DatabaseManager.build_oracle_uri(
                                selected_conn["user"], selected_conn["password"],
                                selected_conn["host"], selected_conn["port"], selected_conn["service"],
                            )
                            st.session_state.oracle_label = f"{selected_conn['name']} ({selected_conn['host']}/{selected_conn['service']})"
                            SessionManager.reset_chat()
                            st.rerun()

                else:
                    st.markdown("##### Yeni Oracle Bağlantısı")
                    new_name = st.text_input("Bağlantı Adı", placeholder="örn: Üretim DB")
                    new_host = st.text_input("Host", placeholder="örn: 192.168.1.10")
                    new_port = st.text_input("Port", value="1521")
                    new_service = st.text_input("Service Name", placeholder="örn: ORCL")
                    new_user = st.text_input("Kullanıcı Adı")
                    new_password = st.text_input("Şifre", type="password")

                    if st.button("💾 Kaydet ve Bağlan", use_container_width=True):
                        if not all([new_name, new_host, new_port, new_service, new_user, new_password]):
                            st.warning("Lütfen tüm alanları doldurun.")
                        elif new_name in conn_names:
                            st.error(f"'{new_name}' adında bir bağlantı zaten mevcut.")
                        else:
                            DatabaseManager.add_oracle_connection(
                                new_name, new_host, new_port, new_service, new_user, new_password
                            )
                            st.session_state.oracle_uri = DatabaseManager.build_oracle_uri(
                                new_user, new_password, new_host, new_port, new_service
                            )
                            st.session_state.oracle_label = f"{new_name} ({new_host}/{new_service})"
                            SessionManager.reset_chat()
                            st.rerun()

                db_uri = st.session_state.get("oracle_uri", "")
                db_label = st.session_state.get("oracle_label", "")

                if db_uri:
                    st.success(f"Bağlı: `{db_label}`")

            if st.session_state.get("active_db") != db_uri:
                st.session_state.active_db = db_uri
                SessionManager.reset_chat()

        return db_uri, db_label

    @staticmethod
    def render_status_panel(db_label: str, db_engine: Optional[SQLDatabase]) -> str:
        with st.sidebar:
            st.markdown("#### 📊 Sistem Durumu")
            if db_engine is not None:
                st.success("Aktif")
            else:
                st.error("Pasif")

            selected_model = st.selectbox(
                "Model Seçin",
                options=AgentManager.CLAUDE_MODELS,
                index=AgentManager.CLAUDE_MODELS.index(AgentManager.MODEL_NAME),
            )
            if st.session_state.get("selected_model") != selected_model:
                st.session_state.selected_model = selected_model
                SessionManager.reset_chat()

            st.markdown("#### 🗂️ Tablolar")
            if db_engine is None:
                st.caption("Bağlantı yok.")
            else:
                try:
                    tables = db_engine.get_usable_table_names()
                    for table in tables:
                        st.markdown(
                            f"<span style='color:#15803d; font-family:monospace; font-weight:500;'>▸ {table}</span>",
                            unsafe_allow_html=True,
                        )
                except Exception:
                    st.caption("Tablolar okunurken hata oluştu.")

            st.markdown("---")
            if st.button("🚪 Çıkış Yap", use_container_width=True):
                from managers.login_manager import LoginManager
                LoginManager.logout()

        return selected_model

    @staticmethod
    def render_chat_interface(agent_executor: Any, db_label: str) -> None:
        st.markdown(
            "<h1 style='color:#15803d;'>🤖 AgenticSQL — Veri Asistanı</h1>",
            unsafe_allow_html=True,
        )
        st.caption(f"Aktif veritabanı: `{db_label}`")

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
                    # Build full message list for LangGraph agent
                    messages = []
                    for msg in st.session_state.messages[:-1]:
                        if msg["role"] == "user":
                            messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            messages.append(AIMessage(content=msg["content"]))
                    messages.append(HumanMessage(content=user_prompt))

                    result = agent_executor.invoke({"messages": messages})
                    answer = result["messages"][-1].content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as error:
                    st.error(f"Analiz sırasında bir sorun çıktı: {error}")
