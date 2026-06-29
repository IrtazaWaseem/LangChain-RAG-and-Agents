import streamlit as st
import pandas as pd
from config.database import get_oracle_conn, get_mongo_conn
from views.dashboard import render_dashboard
from views.build_pc import render_build_pc
from views.compatibility import render_compatibility
from views.submit_benchmark import render_submit_benchmark
from views.admin import render_admin
from views.chatbot import render_chatbot
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
st.set_page_config(page_title="PC Benchmark Registry", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

if "user_rig" not in st.session_state:
    st.session_state.user_rig = {"CPU": "Not Selected", "GPU": "Not Selected", "RAM": "Not Selected", "OS": "Not Selected"}

sql_conn = get_oracle_conn()
mongo_collection = get_mongo_conn()

@st.cache_data(ttl=600)
def get_dropdown_data(table_name, column_name):
    if sql_conn:
        try:
            df = pd.read_sql(f"SELECT {column_name} FROM {table_name}", con=sql_conn)
            return sorted(df=[column_name].tolist())
        except: return ["Data Read Error"]
    return ["SQL Engine Offline"]

@st.cache_data(ttl=60)
def fetch_global_telemetry():
    if mongo_collection is not None:
        raw_data = list(mongo_collection.find({}, {"_id": 0}))
        if raw_data:
            return pd.DataFrame([{
                "Build ID": int(log.get("sql_references", {}).get("build_id", 0)),
                "Game ID": int(log.get("sql_references", {}).get("game_id", 0)),
                "Resolution": str(log.get("game_settings", {}).get("resolution", "N/A")),
                "Preset": str(log.get("game_settings", {}).get("graphics_preset", "N/A")),
                "Avg FPS": float(log.get("performance_metrics", {}).get("fps", {}).get("average_fps", 0)),
                "Min FPS": float(log.get("performance_metrics", {}).get("fps", {}).get("one_percent_low", 0)),
                "GPU Temp (°C)": float(log.get("performance_metrics", {}).get("hardware_telemetry", {}).get("gpu_max_temp_c", 0)),
                "CPU Load (%)": float(log.get("performance_metrics", {}).get("hardware_telemetry", {}).get("cpu_load_pct", 0)),
                "User Notes": str(log.get("user_notes", "N/A"))
            } for log in raw_data])
    return pd.DataFrame()

def clear_caches():
    st.cache_data.clear()

df_global_logs = fetch_global_telemetry()

st.sidebar.markdown("<h1 style='font-size: 2.2rem;'>PC BENCHMARK</h1>", unsafe_allow_html=True)
st.sidebar.divider()
app_mode = st.sidebar.radio("MAIN NAVIGATION", ["Dashboard Overview", "Build a PC", "Compatibility Engine", "Submit Benchmark", "AI Hardware Advisor", "Database Administration"])
st.sidebar.divider()

if app_mode == "Dashboard Overview":
    render_dashboard(sql_conn,df_global_logs)
elif app_mode == "Build a PC":
    render_build_pc(sql_conn)
elif app_mode == "Compatibility Engine":
    render_compatibility(sql_conn, mongo_collection, get_dropdown_data, df_global_logs)
elif app_mode == "Submit Benchmark":
    render_submit_benchmark(sql_conn, mongo_collection, get_dropdown_data, clear_caches)
elif app_mode == "Database Administration":
    render_admin(sql_conn, clear_caches)
elif app_mode == "AI Hardware Advisor":
    render_chatbot(sql_conn)