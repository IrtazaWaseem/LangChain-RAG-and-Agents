import os
import oracledb
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
def get_oracle_conn():
    try:
        user = os.getenv("ORACLE_USER")
        password = os.getenv("ORACLE_PASS")
        dsn = os.getenv("ORACLE_DSN")
        return oracledb.connect(user=user, password=password, dsn=dsn)
    except Exception as e:
        print(f"Oracle Connection Error: {e}")
        return None

def get_mongo_conn():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri)
        return client["pc_benchmark_logs"]["Performance_Logs"]
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        return None