import os
import glob
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(page_title="AgenticSQL", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
    /* Main Application Background Themes*/
    .stApp { background-color: #0d1117; }

    /* Slider Bar (white themes) */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #e6e8eb;
    }
    /* Sidebar Text Color */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #1f2328 !important;
    }
    /* Sidebar Selectbox & Input Area */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #f6f8fa !important;
        color: #1f2328 !important;
    }

    /* CHAT Area (dark themes) */
    [data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }
    .stMarkdown p { color: #e6edf3 !important; }

    /* Footer & Divider */
    hr { border-color: #30363d !important; }
    </style>
    """, unsafe_allow_html=True)


# All DB List
def get_available_databases():
    if not os.path.exists("Database"):
        os.makedirs("Database")
    files = glob.glob("Database/*.sqlite") + glob.glob("Database/*.db")
    return [os.path.basename(f) for f in files]


@st.cache_resource
def init_agent(db_path):
    if not os.path.exists(db_path):
        return None, None

    db_engine = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    custom_suffix = """
    Her zaman sorgu yazmadan önce veritabanı şemasını dikkatlice incele. 
    Eğer soruyla ilgili yeterli bilgi yoksa, varsayımda bulunma, kullanıcıya sor.
    Veritabanı üzerinde DROP, DELETE veya ALTER komutlarını kesinlikle kullanamazsın.
    Sonuçları her zaman kullanıcı dostu bir Türkçe ile açıkla.
    """

    agent_executor = create_sql_agent(
        llm,
        db=db_engine,
        agent_type="openai-tools",
        verbose=True,
        suffix=custom_suffix
    )
    return agent_executor, db_engine


# Sidebar dynamic select
with st.sidebar:
    st.title("📟 AgenticSQL")
    st.markdown("---")

    databases = get_available_databases()

    if databases:
        selected_db_file = st.selectbox(
            "Veritabanı Seçin",
            options=databases,
            index=0
        )
        current_db_path = os.path.join("Database", selected_db_file)
    else:
        st.error("Lütfen 'Database' klasörüne bir veritabanı dosyası ekleyin.")
        st.stop()

    if "active_db" not in st.session_state:
        st.session_state.active_db = current_db_path

    if st.session_state.active_db != current_db_path:
        st.session_state.active_db = current_db_path
        st.session_state.messages = []  # new db for clean chat
        st.session_state.store = {}  # new db for clean memory
        st.cache_resource.clear()  # rerun agent
        st.rerun()

    # Start Agent
    agent_executor, db_engine = init_agent(current_db_path)

    st.subheader("📊 Sistem Durumu")
    st.success(f"Aktif: `{selected_db_file}`")

    st.subheader("🗂️ Tablo Listesi")
    try:
        tables = db_engine.get_usable_table_names()
        for table in tables:
            st.markdown(f"- `{table}`")
    except Exception as e:
        st.caption("Tablolar okunurken hata oluştu.")

    st.markdown("---")
    if st.button("Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.session_state.store = {}
        st.rerun()

if "store" not in st.session_state:
    st.session_state.store = {}

if "messages" not in st.session_state:
    st.session_state.messages = []


def get_session_history(session_id: str):
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]


# Agent with History Wrap
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Main UI
st.title("🤖 SQL Agent: Enterprise Data Interface")
st.caption(f"Su anda `{selected_db_file}` üzerinde çalışıyorsunuz.")

# Write Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Veritabanına bir soru sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Veri ambarı taranıyor..."):
            try:
                session_id = f"session_{selected_db_file}"
                config = {"configurable": {"session_id": session_id}}

                response = agent_with_chat_history.invoke({"input": prompt}, config)
                answer = response["output"]

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"Analiz sırasında bir sorun çıktı: {str(e)}")


st.markdown("---")
st.caption("© 2026 AgenticSQL")