import streamlit as st


class SessionManager:
    @staticmethod
    def ensure_state() -> None:
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @staticmethod
    def reset_chat() -> None:
        st.session_state.messages = []
        st.cache_resource.clear()
        st.rerun()
