import streamlit as st
import pandas as pd
from core.engines import HardwareScoringEngine, CompatibilityEngine, FPSPredictionEngine, UpgradeRecommendationEngine
from ui.charts import build_spec_compliance_comparison, build_frame_time_variance


def render_compatibility(sql_conn, mongo_collection, get_dropdown_data, df_global_logs):
    st.title("COMPATIBILITY INTELLIGENCE HUB")
    st.divider()

    if "user_rig" not in st.session_state or st.session_state.user_rig["CPU"] == "Not Selected" or \
            st.session_state.user_rig["GPU"] == "Not Selected":
        st.warning("Hardware profile unassigned. Please define system components inside the Build a PC portal.")
        return

    if not sql_conn:
        st.error("Infrastructure Error: Communication channel to relational catalog engine lost.")
        return

    scorer = HardwareScoringEngine()
    engine = CompatibilityEngine(sql_conn, scorer)
    predictor = FPSPredictionEngine()
    optimizer = UpgradeRecommendationEngine(predictor)

    with st.form("compatibility_analysis_form"):
        st.subheader("Select Benchmark Target")
        target_title = st.selectbox("Target Application Software:", get_dropdown_data("GAMES", "TITLE"))
        analyze_btn = st.form_submit_button("Run Hardware Analysis", type="primary")

    if analyze_btn:
        try:
            df_u_gpu = pd.read_sql("SELECT BENCHMARK_SCORE, VRAM_GB FROM GPUS WHERE MODEL = :1", con=sql_conn,
                                   params=[st.session_state.user_rig["GPU"]])
            df_u_cpu = pd.read_sql("SELECT BENCHMARK_SCORE FROM CPUS WHERE MODEL = :1", con=sql_conn,
                                   params=[st.session_state.user_rig["CPU"]])

            user_build = {
                "gpu_score": float(df_u_gpu["BENCHMARK_SCORE"].iloc[0]),
                "vram_gb": float(df_u_gpu["VRAM_GB"].iloc[0]),
                "cpu_score": float(df_u_cpu["BENCHMARK_SCORE"].iloc[0]),
                "ram_capacity": float(st.session_state.user_rig["RAM"].split("GB")[0])
            }

            report = engine.evaluate(target_title, user_build)
            game_req = report["game_req"]

            telemetry_list = []
            if mongo_collection is not None:
                telemetry_list = list(mongo_collection.find({"sql_references.game_id": game_req["game_id"]}))

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #ffaa00;">
                    <h4 style="color: #ffaa00; margin-top:0;">MINIMUM SPECIFICATIONS</h4><hr style="border-color:#333;">
                    <b>CPU baseline:</b> {game_req['min_cpu_m']}<br>
                    <b>GPU baseline:</b> {game_req['min_gpu_m']}<br>
                    <b>Memory Constraint:</b> {game_req['min_ram']} GB<br>
                    <b>Texture Constraint:</b> {game_req['min_vram']} GB VRAM
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #00ccff;">
                    <h4 style="color: #00ccff; margin-top:0;">RECOMMENDED SPECIFICATIONS</h4><hr style="border-color:#333;">
                    <b>CPU baseline:</b> {game_req['rec_cpu_m']}<br>
                    <b>GPU baseline:</b> {game_req['rec_gpu_m']}<br>
                    <b>Memory Constraint:</b> {game_req['rec_ram']} GB<br>
                    <b>Texture Constraint:</b> {game_req['rec_vram']} GB VRAM
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            st.subheader("Can I Run It? Analysis Panel")
            s_color = {"BELOW MINIMUM": "#ff3333", "MINIMUM READY": "#ffaa00", "RECOMMENDED READY": "#00ccff",
                       "ULTRA READY": "#cc00ff"}[report["status_level"]]

            st.markdown(f"""
            <div style="border: 3px solid {s_color}; border-radius: 12px; padding: 35px; text-align: center; background: rgba(5,5,10,0.8); box-shadow: 0 0 25px {s_color}25;">
                <h2 style="color: {s_color}; margin:0; font-weight:900;">{report['status_level']}</h2>
                <p style="font-size:1.3rem; margin-top:8px; color:#e2e8f0;">Dynamic Integration Index Score: <b>{report['composite_score']} / 100</b></p>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            st.subheader("Render Metrics Forecast Tuning")
            sc1, sc2 = st.columns(2)
            t_res = sc1.selectbox("Resolution Target Override:", ["1080p", "1440p", "4K"])
            t_pre = sc2.selectbox("Graphics Pipeline Quality Preset:", ["Low", "Medium", "High", "Ultra"])

            pred = predictor.predict(telemetry_list, user_build, t_res, t_pre)
            opt_set = optimizer.find_optimal_settings(telemetry_list, user_build)

            st.success(
                f"Predicted Engine Performance: {pred['avg_fps']} FPS Average | {pred['min_fps']} FPS 1% Lows ({pred['confidence']})")

            if mongo_collection is not None:
                new_log = {
                    "sql_references": {"game_id": game_req["game_id"]},
                    "hardware_profile": {
                        "cpu_model": st.session_state.user_rig["CPU"],
                        "gpu_model": st.session_state.user_rig["GPU"],
                        "ram_gb": user_build["ram_capacity"]
                    },
                    "game_settings": {
                        "resolution": t_res,
                        "graphics_preset": t_pre
                    },
                    "performance_metrics": {
                        "fps": {
                            "average_fps": pred['avg_fps'],
                            "one_percent_low": pred['min_fps']
                        },
                        "gpu_temperature_c": 75
                    }
                }
                existing = mongo_collection.find_one({
                    "sql_references.game_id": game_req["game_id"],
                    "hardware_profile.cpu_model": st.session_state.user_rig["CPU"],
                    "hardware_profile.gpu_model": st.session_state.user_rig["GPU"],
                    "game_settings.resolution": t_res,
                    "game_settings.graphics_preset": t_pre
                })
                if not existing:
                    mongo_collection.insert_one(new_log)

                    new_row = pd.DataFrame([{
                        'Avg FPS': pred['avg_fps'],
                        'GPU Temp (°C)': 75,
                        'Preset': t_pre,
                        'Game Title': target_title,
                        'Resolution': t_res
                    }])

                    if 'df_global_logs' in st.session_state:
                        st.session_state['df_global_logs'] = pd.concat([st.session_state['df_global_logs'], new_row],
                                                                       ignore_index=True)

                    st.success("Telemetry log successfully broadcasted to background analytical systems!")

            st.divider()

            st.subheader("Optimization & Hardware Upgrade Matrix")
            o_col1, o_col2 = st.columns(2)
            with o_col1:
                st.markdown(f"""
                <div style="padding:22px; border-radius:8px; background:rgba(0, 204, 255, 0.08); border-left:5px solid #00ccff; height:100%;">
                    <h5 style="margin:0; color:#00ccff;">SWEET-SPOT SETTING TARGETS</h5>
                    <p style="margin-top:8px;">Achieve stable <b>60+ FPS</b> execution on current hardware configurations by matching this render configuration:</p>
                    <b>Target Resolution:</b> {opt_set['resolution']}<br>
                    <b>Quality Preset:</b> {opt_set['preset']}<br>
                    <b>Projected Smoothness Index:</b> {opt_set['avg_fps']} FPS
                </div>
                """, unsafe_allow_html=True)
            with o_col2:
                st.markdown("<h5 style='margin-bottom: 15px;'>Diagnostic Bottleneck Dispatches</h5>",
                            unsafe_allow_html=True)
                ups = optimizer.generate_upgrades(user_build, game_req)
                if not ups:
                    st.success(
                        "Balanced microarchitecture composition verified. Zero pipeline bottleneck constraints found.")
                else:
                    for u in ups:
                        st.markdown(f"""
                        <div style='padding:12px; margin-bottom:10px; border-radius:4px; background:rgba(255,51,51,0.05); border-left:4px solid #ff3333;'>
                            <b style='color:#ffaa00;'>{u['component']}:</b> {u['issue']}<br>
                            <span style='color:#00ff99;'>Fix:</span> {u['fix']}
                        </div>
                        """, unsafe_allow_html=True)

            st.divider()

            st.subheader("Interactive WebGL Compliance Analysis")
            u_scores = {'gpu': user_build['gpu_score'], 'cpu': user_build['cpu_score'],
                        'ram_raw': user_build['ram_capacity'], 'vram_raw': user_build['vram_gb']}

            chart_tab1, chart_tab2 = st.tabs(["Compliance Distributions", "Render Consistency Box Metrics"])
            with chart_tab1:
                st.plotly_chart(build_spec_compliance_comparison(u_scores, game_req), use_container_width=True)
            with chart_tab2:
                if not df_global_logs.empty:
                    st.plotly_chart(build_frame_time_variance(df_global_logs), use_container_width=True)
                else:
                    st.info("Awaiting telemetry data to render frame-time variance graph.")

        except Exception as ex:
            st.error(f"Error executing SQL engine compute functions: {str(ex)}")