import os
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
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
Sonuçları her zaman kullanıcı dostu bir Türkçe ile açıkla.
"""



# create agent
agent_executor = create_sql_agent(
    llm,
    db=db,
    agent_type="openai-tools",
    verbose=True,
    custom_suffix=custom_suffix
)

response = agent_executor.invoke({"input": "Veritabanındaki tabloları listele ve her tabloda kaç satır olduğunu söyle."})
print(response["output"])