import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv

# --- CONFIG & SETUP ---
load_dotenv()
st.set_page_config(page_title="AgenticSQL", layout="wide", page_icon="🤖")

# Custom CSS: Terminal Estetiği
st.markdown("""
    <style>
    /* Ana arka plan koyu kalsın (Odaklanma için) */
    .stApp {
        background-color: #0d1117;
    }

    /* SOL MENÜ (Sidebar) BEYAZ TASARIM */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important; /* Arka plan bembeyaz */
        border-right: 1px solid #e6e8eb;
    }

    /* Sol menü içindeki yazıları koyu yap (Okunabilirlik için) */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: #1f2328 !important;
    }

    /* Sol menüdeki ikonlar ve buton metinleri */
    [data-testid="stSidebar"] .stButton button {
        color: #1f2328 !important;
        border: 1px solid #d0d7de;
    }

    /* Chat mesaj kutuları (Koyu modda devam) */
    [data-testid="stChatMessage"] {
        background-color: #1d222b !important;
        border: 1px solid #30363d !important;
    }

    .stMarkdown p {
        color: #e6edf3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND INITIALIZATION ---
DB_PATH = "Database/Chinook_Sqlite.sqlite"


@st.cache_resource
def init_agent():
    if not os.path.exists(DB_PATH):
        st.error(f"Hata: {DB_PATH} dosyası bulunamadı!")
        return None

    db_engine = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
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
        suffix=custom_suffix  # Sende custom_suffix değişkeniydi, fonksiyonda parametre adı 'suffix'dir
    )
    return agent_executor, db_engine


agent_executor, db_engine = init_agent()

# Mesaj Geçmişi (Session State)
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

# --- UI LAYOUT ---
with st.sidebar:
    st.title("📟 AgenticSQL")
    st.markdown("---")
    st.subheader("📊 Sistem Durumu")
    st.success("Veritabanı: Aktif")
    st.info(f"Dosya: `{DB_PATH.split('/')[-1]}`")

    st.subheader("🗂️ Mevcut Tablolar")
    try:
        tables = db_engine.get_usable_table_names()
        for table in tables:
            st.markdown(f"- `{table}`")
    except:
        st.write("Tablo listesi alınamadı.")

    st.markdown("---")
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.session_state.store = {}
        st.rerun()

# Ana Ekran
st.title("🤖 SQL Agent: Enterprise Data Interface")
st.caption("Doğal dilden SQL'e mimari köprü")

# Mesajları Görüntüle
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Veritabanına bir soru sor (Örn: En çok kazandıran sanatçı kim?)"):
    # Mesajı ekrana bas ve kaydet
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Yanıtı
    with st.chat_message("assistant"):
        with st.spinner("Agent veritabanı üzerinde akıl yürütüyor..."):
            config = {"configurable": {"session_id": "agenticsql_streamlit_session"}}

            # Agent'ı çalıştır
            try:
                response = agent_with_chat_history.invoke({"input": prompt}, config)
                full_response = response["output"]

                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")

# --- FOOTER ---
st.markdown("---")
st.caption("Built for Professional Data Architects | 2026")