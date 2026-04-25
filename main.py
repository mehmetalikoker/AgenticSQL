import os
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv

load_dotenv()

db = "Database/Chinook_Sqlite.sqlite"
connection = sqlite3.connect(db)

if not os.path.exists(db):
    print(f"Hata: {db} dosyası bulunamadı! Lütfen dosya adını kontrol edin.")
else:

    db = SQLDatabase.from_uri(f"sqlite:///{db}")
    print("SQLDatabase nesnesi başarıyla oluşturuldu.")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

custom_suffix = """
Her zaman sorgu yazmadan önce veritabanı şemasını dikkatlice incele. 
Eğer soruyla ilgili yeterli bilgi yoksa, varsayımda bulunma, kullanıcıya sor.
Veritabanı üzerinde DROP, DELETE veya ALTER komutlarını kesinlikle kullanamazsın.
Sonuçları her zaman kullanıcı dostu bir Türkçe ile açıkla.
"""

config = {
    "configurable": {
        "session_id": "agenticsql_sessionID"
    }
}
store = {}

def get_session_history(agenticsql_sessionID: str):
    if agenticsql_sessionID not in store:
        store[agenticsql_sessionID] = ChatMessageHistory()
    return store[agenticsql_sessionID]


# create agent
agent_executor = create_sql_agent(
    llm,
    db=db,
    agent_type="openai-tools",
    verbose=True,
    custom_suffix=custom_suffix
)
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

response = agent_with_chat_history.invoke({"input": "Veritabanındaki tabloları listele ve her tabloda kaç satır olduğunu söyle."},config)
print(response["output"])