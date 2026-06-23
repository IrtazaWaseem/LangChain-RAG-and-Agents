import streamlit as st
import pandas as pd

def render_submit_benchmark(sql_conn, mongo_collection, get_dropdown_data, clear_cache_func):
    st.title("SUBMIT SYSTEM PERFORMANCE")
    st.markdown("JSON Telemetry Ingestion Node")
    st.divider()

    if mongo_collection is None:
        st.error("NoSQL Database offline. Input submission pathways locked.")
    else:
        with st.form("telemetry_ingestion_form"):
            g_target = st.selectbox("Select Target Application Software:", get_dropdown_data("GAMES", "TITLE"))

            c_left, c_right = st.columns(2)
            res_target = c_left.selectbox("Resolution Target Metric:", ["1080p", "1440p", "4K"])
            pre_target = c_right.selectbox("Graphics Pipeline Layout Preset:", ["Low", "Medium", "High", "Ultra"])

            fps_avg = st.number_input("Average Frames Per Second (FPS):", min_value=1, value=60)
            fps_min = st.number_input("1% Minimum Frame Drops (FPS):", min_value=1, value=45)

            t_gpu = st.number_input("Peak Core GPU Temperature Load (°C):", min_value=30, value=72)
            u_cpu = st.number_input("Central Processor Core Load Utilization (%):", min_value=1, max_value=100, value=45)

            notes = st.text_area("User Operational Logs & Dynamic Graphical Settings (e.g., Ray Tracing On, DLSS Quality):")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Submit Telemetry Data"):
                game_id_val = 1
                if sql_conn:
                    try:
                        df_g = pd.read_sql("SELECT GAME_ID FROM GAMES WHERE TITLE = :1", con=sql_conn, params=[g_target])
                        game_id_val = int(df_g["GAME_ID"].iloc[0])
                    except:
                        pass

                document = {
                    "sql_references": {"user_id": 1, "build_id": 4, "game_id": game_id_val},
                    "game_settings": {"resolution": res_target, "graphics_preset": pre_target},
                    "performance_metrics": {
                        "fps": {"average_fps": int(fps_avg), "one_percent_low": int(fps_min)},
                        "hardware_telemetry": {"gpu_max_temp_c": int(t_gpu), "cpu_load_pct": int(u_cpu)}
                    },
                    "user_notes": notes
                }

                mongo_collection.insert_one(document)
                clear_cache_func()
                st.success("JSON telemetry payload verified and written to MongoDB log storage.")