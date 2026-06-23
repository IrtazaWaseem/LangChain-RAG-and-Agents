import streamlit as st
import pandas as pd


def render_build_pc(sql_conn):
    st.title("CONFIGURE SYSTEM HARDWARE")
    st.text("Profile Registration Registry")
    st.divider()

    if "user_rig" not in st.session_state or "SSD" not in st.session_state.user_rig:
        st.session_state.user_rig = {
            "CPU": "Not Assigned",
            "GPU": "Not Assigned",
            "RAM": "Not Assigned",
            "SSD": "Not Assigned",
            "OS": "Not Assigned",
            "Tier": "Unranked"
        }

    if sql_conn:
        try:
            df_cpus = pd.read_sql("SELECT MODEL FROM CPUS ORDER BY MODEL", con=sql_conn)
            cpus = df_cpus['MODEL'].tolist() if not df_cpus.empty else ["Database Error"]

            df_gpus = pd.read_sql("SELECT MODEL FROM GPUS ORDER BY MODEL", con=sql_conn)
            gpus = df_gpus['MODEL'].tolist() if not df_gpus.empty else ["Database Error"]

            df_ram = pd.read_sql(
                "SELECT Capacity_GB || 'GB ' || DDR_Generation AS RAM_LABEL FROM RAM_CONFIGURATIONS ORDER BY Capacity_GB",
                con=sql_conn)
            rams = df_ram['RAM_LABEL'].tolist() if not df_ram.empty else ["Database Error"]

            df_os = pd.read_sql(
                "SELECT OS_Name || ' (' || Architecture || ')' AS OS_LABEL FROM OPERATING_SYSTEMS ORDER BY OS_Name",
                con=sql_conn)
            oses = df_os['OS_LABEL'].tolist() if not df_os.empty else ["Database Error"]

            df_ssd = pd.read_sql(
                "SELECT Brand || ' ' || Model || ' (' || Capacity_GB || 'GB)' AS SSD_LABEL FROM SSDS ORDER BY Capacity_GB",
                con=sql_conn)
            ssds = df_ssd['SSD_LABEL'].tolist() if not df_ssd.empty else ["Database Error"]

        except Exception as e:
            st.error(f"Database Error: {str(e)}")
            cpus, gpus, rams, oses, ssds = ["Error"], ["Error"], ["Error"], ["Error"], ["Error"]
    else:
        st.error("Oracle database controller offline.")
        return

    f_col, d_col = st.columns([2, 1], gap="large")

    with f_col:
        with st.form("hardware_registration"):
            c_sel = st.selectbox("Assign Processor (CPU):", cpus)
            g_sel = st.selectbox("Assign Graphics Accelerator (GPU):", gpus)
            r_sel = st.selectbox("Assign System Memory Allocation:", rams)
            s_sel = st.selectbox("Assign Solid State Drive (SSD):", ssds)
            o_sel = st.selectbox("Assign Primary Operational Environment:", oses)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save System Configuration"):
                try:
                    t_cpu = \
                    pd.read_sql("SELECT Tier_ID FROM CPUS WHERE MODEL = :1", con=sql_conn, params=[c_sel]).iloc[0][
                        'TIER_ID']
                    t_gpu = \
                    pd.read_sql("SELECT Tier_ID FROM GPUS WHERE MODEL = :1", con=sql_conn, params=[g_sel]).iloc[0][
                        'TIER_ID']
                    t_ssd = pd.read_sql(
                        "SELECT Tier_ID FROM SSDS WHERE Brand || ' ' || Model || ' (' || Capacity_GB || 'GB)' = :1",
                        con=sql_conn, params=[s_sel]).iloc[0]['TIER_ID']

                    avg_tier = round((t_cpu + t_gpu + t_ssd) / 3)
                    tier_name = pd.read_sql("SELECT Tier_Name FROM HARDWARE_TIERS WHERE Tier_ID = :1", con=sql_conn,
                                            params=[avg_tier]).iloc[0]['TIER_NAME']
                except Exception:
                    tier_name = "Unranked"

                st.session_state.user_rig = {
                    "CPU": c_sel,
                    "GPU": g_sel,
                    "RAM": r_sel,
                    "SSD": s_sel,
                    "OS": o_sel,
                    "Tier": tier_name
                }
                st.success(
                    "Hardware configuration initialized and cached successfully inside active runtime memory session.")

    with d_col:
        st.text("Verified System Footprint")

        st.info(f"Processor Node: {st.session_state.user_rig['CPU']}")
        st.info(f"Graphics Core: {st.session_state.user_rig['GPU']}")
        st.info(f"RAM Allocation: {st.session_state.user_rig['RAM']}")
        st.info(f"Storage Array: {st.session_state.user_rig['SSD']}")
        st.info(f"OS Environment: {st.session_state.user_rig['OS']}")

        t_color = "cyan" if st.session_state.user_rig['Tier'] in ["Enthusiast", "Mid-Range"] else "orange"

        st.markdown(f"""
        <div style="border: 2px solid {t_color}; border-radius: 8px; padding: 15px; text-align: center; background: rgba(255,255,255,0.05); margin-top: 15px;">
            <h5 style="color: {t_color}; margin:0;">HARDWARE TIER RATING</h5>
            <h3 style="margin-top:5px; margin-bottom:0; color:whitesmoke;">{st.session_state.user_rig['Tier']}</h3>
        </div>
        """, unsafe_allow_html=True)