import os
from typing import Any, Optional, Tuple

import streamlit as st
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_anthropic import ChatAnthropic


class AgentManager:
    PAGE_TITLE = "AgenticSQL"
    PAGE_ICON = "🤖"
    MODEL_NAME = "claude-sonnet-4-6"
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
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

            html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

            /* Ana alan - beyaz tema */
            .stApp {
                background-color: #f8fafc;
            }

            /* Sol sidebar - beyaz, okunur */
            [data-testid="stSidebar"] {
                background-color: #ffffff !important;
                border-right: 2px solid #16a34a !important;
                box-shadow: 2px 0 8px rgba(0,0,0,0.06);
            }
            [data-testid="stSidebar"] .stMarkdown p,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] label {
                color: #1e293b !important;
                font-size: 0.9rem;
            }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: #15803d !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] > div {
                background-color: #f0fdf4 !important;
                border: 1px solid #86efac !important;
                color: #1e293b !important;
            }
            [data-testid="stSidebar"] hr {
                border-color: #dcfce7 !important;
            }

            /* Sidebar butonları */
            [data-testid="stSidebar"] .stButton > button {
                background-color: #16a34a !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                transition: background 0.2s ease;
            }
            [data-testid="stSidebar"] .stButton > button:hover {
                background-color: #15803d !important;
            }

            /* Ana alan - sağ içerik */
            .main .block-container {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 2rem 2.5rem;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            }

            /* Başlıklar */
            h1 { color: #15803d !important; }
            h2, h3 { color: #1e293b !important; }
            .stCaption { color: #64748b !important; }

            /* Chat mesajları */
            [data-testid="stChatMessage"] {
                background-color: #f0fdf4 !important;
                border: 1px solid #bbf7d0 !important;
                border-radius: 10px !important;
                margin-bottom: 8px !important;
            }

            /* Chat input */
            [data-testid="stChatInput"] textarea {
                background-color: #ffffff !important;
                border: 1.5px solid #16a34a !important;
                color: #1e293b !important;
                border-radius: 10px !important;
            }
            [data-testid="stChatInput"] textarea::placeholder { color: #94a3b8 !important; }

            /* Metin */
            .stMarkdown p { color: #334155 !important; }

            /* Alert */
            [data-testid="stAlert"] { border-radius: 8px !important; }

            /* Divider */
            hr { border-color: #e2e8f0 !important; }

            /* Spinner */
            .stSpinner > div { border-top-color: #16a34a !important; }

            /* Scrollbar */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: #f1f5f9; }
            ::-webkit-scrollbar-thumb { background: #86efac; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #16a34a; }
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
        llm = ChatAnthropic(model=AgentManager.MODEL_NAME)

        agent_executor = create_sql_agent(
            llm,
            db=db_engine,
            agent_type="tool-calling",
            verbose=True,
            suffix=AgentManager.CUSTOM_AGENT_SUFFIX,
        )

        return agent_executor, db_engine
