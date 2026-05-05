import os
from typing import Any, Optional, Tuple

import streamlit as st
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI


class AgentManager:
    PAGE_TITLE = "AgenticSQL"
    PAGE_ICON = "🤖"
    MODEL_NAME = "gpt-4o"
    DEFAULT_TEMPERATURE = 0
    CUSTOM_AGENT_SUFFIX = """
Her zaman sorgu yazmadan önce veritabanı şemasını dikkatlice incele.
Eğer soruyla ilgili yeterli bilgi yoksa, varsayımda bulunma, kullanıcıya sor.
Veritabanı üzerinde DROP, DELETE veya ALTER komutlarını kesinlikle kullanamazsın.
Sonuçları her zaman kullanıcı dostu bir Türkçe ile açıkla.
"""

    @staticmethod
    def setup_page() -> None:
        st.set_page_config(
            page_title=AgentManager.PAGE_TITLE,
            layout="wide",
            page_icon=AgentManager.PAGE_ICON,
        )
        st.markdown(
            """
            <style>
            .stApp { background-color: #0d1117; }
            [data-testid="stSidebar"] {
                background-color: #FFFFFF !important;
                border-right: 1px solid #e6e8eb;
            }
            [data-testid="stSidebar"] .stMarkdown p,
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
                color: #1f2328 !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] > div {
                background-color: #f6f8fa !important;
                color: #1f2328 !important;
            }
            [data-testid="stChatMessage"] {
                background-color: #161b22 !important;
                border: 1px solid #30363d !important;
            }
            .stMarkdown p { color: #e6edf3 !important; }
            hr { border-color: #30363d !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    @st.cache_resource
    def init_agent(db_path: str) -> Tuple[Optional[Any], Optional[SQLDatabase]]:
        if not os.path.exists(db_path):
            return None, None

        db_engine = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        llm = ChatOpenAI(
            model=AgentManager.MODEL_NAME,
            temperature=AgentManager.DEFAULT_TEMPERATURE,
        )

        agent_executor = create_sql_agent(
            llm,
            db=db_engine,
            agent_type="openai-tools",
            verbose=True,
            suffix=AgentManager.CUSTOM_AGENT_SUFFIX,
        )

        return agent_executor, db_engine
