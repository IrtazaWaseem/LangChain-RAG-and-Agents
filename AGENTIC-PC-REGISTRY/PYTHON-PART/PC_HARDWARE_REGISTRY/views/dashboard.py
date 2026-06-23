import streamlit as st
import pandas as pd
from ui.charts import build_fps_gauge, build_thermal_gauge, build_frame_time_variance


def render_dashboard(sql_conn, df_global_logs):
    st.title("PLATFORM OVERVIEW")
    st.text("Real-Time Benchmark Infrastructure Feed")
    st.divider()

    if sql_conn:
        try:
            st.subheader("Registered Game Engine Ecosystem")
            query_games = """
                SELECT 
                    g.Title, 
                    g.Developer, 
                    g.Release_Year, 
                    c.Category_Name AS Category, 
                    g.Storage_Required_GB 
                FROM GAMES g
                LEFT JOIN GAME_CATEGORIES c ON g.Category_ID = c.Category_ID
                ORDER BY g.Game_ID
            """
            df_games = pd.read_sql(query_games, con=sql_conn)

            if not df_games.empty:
                st.dataframe(df_games, width="stretch", hide_index=True)
            else:
                st.info("GAMES table is connected but empty.")

            st.divider()

            st.subheader("Core Hardware Registries")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Central Processing Units (CPUs)")
                query_cpus = "SELECT Brand, Model, Core_Count, Boost_Clock_GHz, Benchmark_Score FROM CPUS ORDER BY CPU_ID"
                df_all_cpus = pd.read_sql(query_cpus, con=sql_conn)

                if not df_all_cpus.empty:
                    st.dataframe(df_all_cpus, width="stretch", hide_index=True)
                else:
                    st.info("CPUS table is empty.")

            with col2:
                st.subheader("Graphics Processing Units (GPUs)")
                query_gpus = "SELECT Brand, Model, VRAM_GB, Power_W, Benchmark_Score FROM GPUS ORDER BY GPU_ID"
                df_all_gpus = pd.read_sql(query_gpus, con=sql_conn)

                if not df_all_gpus.empty:
                    st.dataframe(df_all_gpus, width="stretch", hide_index=True)
                else:
                    st.info("GPUS table is empty.")

        except Exception as e:
            st.error(f"Oracle Infrastructure Mapping Error: {str(e)}")
    else:
        st.error("No active Oracle SQL connection context found.")

    st.divider()
    st.subheader("Global Telemetry Analytics")
    st.caption("Aggregated from background MongoDB ingestion streams")

    if df_global_logs is not None and not df_global_logs.empty:
        avg_display_fps = df_global_logs['Avg FPS'].mean()
        avg_display_temp = df_global_logs['GPU Temp (°C)'].mean()

        gauge_col1, gauge_col2 = st.columns(2)
        with gauge_col1:
            st.plotly_chart(build_fps_gauge(int(avg_display_fps)), use_container_width=True)
        with gauge_col2:
            st.plotly_chart(build_thermal_gauge(int(avg_display_temp)), use_container_width=True)

        st.plotly_chart(build_frame_time_variance(df_global_logs), use_container_width=True)
    else:
        st.info("System awaiting background performance data ingestion to generate visual analytics.")