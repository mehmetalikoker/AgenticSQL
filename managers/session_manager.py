import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory


class SessionManager:
    @staticmethod
    def ensure_state() -> None:
        if "store" not in st.session_state:
            st.session_state.store = {}
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @staticmethod
    def reset_chat() -> None:
        st.session_state.messages = []
        st.session_state.store = {}
        st.cache_resource.clear()
        st.rerun()

    @staticmethod
    def get_history(session_id: str) -> ChatMessageHistory:
        store = st.session_state.store
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]
