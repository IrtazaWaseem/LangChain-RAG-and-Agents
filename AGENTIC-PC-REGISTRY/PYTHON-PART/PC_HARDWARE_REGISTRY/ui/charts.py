import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def build_fps_bar_chart(fps_data: pd.DataFrame) -> go.Figure:
    if fps_data.empty or 'Resolution' not in fps_data.columns or 'Avg FPS' not in fps_data.columns:
        return go.Figure()
    fig = go.Figure(data=[
        go.Bar(
            x=fps_data['Resolution'],
            y=fps_data['Avg FPS'],
            marker_color=['green', 'cyan', 'magenta'],
            text=fps_data['Avg FPS'].round(1),
            textposition='auto'
        )
    ])
    fig.update_layout(
        title="Average Framerate by Resolution Target",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="lightgray", family="Rajdhani"),
        xaxis=dict(showgrid=False, title="Resolution Target"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title="Frames Per Second (FPS)")
    )
    return fig


def build_fps_gauge(fps_value: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fps_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Average FPS", 'font': {'size': 24, 'color': 'green'}},
        gauge={
            'axis': {'range': [None, 300], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "green"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(255, 51, 51, 0.3)'},
                {'range': [60, 144], 'color': 'rgba(0, 204, 255, 0.3)'},
                {'range': [144, 300], 'color': 'rgba(0, 255, 153, 0.3)'}],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 240}
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="lightgray", family="Rajdhani"), height=350)
    return fig


def build_thermal_gauge(temp_value: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temp_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "GPU Peak Temp (°C)", 'font': {'size': 24, 'color': 'red'}},
        gauge={
            'axis': {'range': [None, 110], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "red"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 65], 'color': 'rgba(0, 255, 153, 0.3)'},
                {'range': [65, 85], 'color': 'rgba(255, 170, 0, 0.3)'},
                {'range': [85, 110], 'color': 'rgba(255, 51, 51, 0.3)'}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="lightgray", family="Rajdhani"), height=350)
    return fig


def build_spec_compliance_comparison(user_scores: dict, game_reqs: dict) -> go.Figure:
    categories = ['GPU Processing', 'CPU Processing', 'RAM Capacity', 'VRAM Allocation']
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Active Hardware Rig', x=categories,
                         y=[user_scores['gpu'], user_scores['cpu'], user_scores['ram_raw'], user_scores['vram_raw']],
                         marker_color='green'))
    fig.add_trace(go.Bar(name='Recommended Profile', x=categories,
                         y=[game_reqs['rec_gpu_score'], game_reqs['rec_cpu_score'], game_reqs['rec_ram'],
                            game_reqs['rec_vram']], marker_color='rgba(255, 255, 255, 0.15)'))
    fig.update_layout(barmode='group', title="Component Specification Compliance Balance", plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font=dict(color="lightgray", family="Rajdhani"))
    return fig


def build_frame_time_variance(df_logs: pd.DataFrame) -> go.Figure:
    if df_logs.empty or 'Avg FPS' not in df_logs.columns or 'Preset' not in df_logs.columns:
        return go.Figure()
    local_df = df_logs.copy()
    local_df["Frame Time (ms)"] = 1000.0 / local_df["Avg FPS"].replace(0, 1)  

    fig = go.Figure()
    fig.add_trace(go.Box(
        x=local_df["Preset"],
        y=local_df["Frame Time (ms)"],
        boxpoints='all',
        jitter=0.4,
        pointpos=-1.8,
        marker_color='green',
        line_color='cyan'
    ))
    fig.update_layout(
        title="Frame-Time Consistency & Latency Fluctuations",
        xaxis_title="Graphics Quality Configuration",
        yaxis_title="Calculated Render Delay (ms)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="lightgray", family="Rajdhani")
    )
    return fig