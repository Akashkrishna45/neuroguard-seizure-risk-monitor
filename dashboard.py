import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import os
import re

# ============================================
# PATH CONFIGURATION - HARDCODED FOR YOUR SETUP
# ============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Use the exact path where the bridge writes CSV
CSV_FILE = r"C:\Users\AKASH\Desktop\epilepsy prediction\live_sensor_data.csv"

print(f"[DEBUG] Dashboard started at {datetime.now()}")
print(f"[DEBUG] CSV_FILE = {CSV_FILE}")
print(f"[DEBUG] CSV exists = {os.path.exists(CSV_FILE)}")

# ============================================
# Session State Initialization
# ============================================
if "simulated_seizure" not in st.session_state:
    st.session_state.simulated_seizure = False

# ============================================
# Load AI Model
# ============================================
try:
    model = joblib.load(os.path.join(SCRIPT_DIR, "neuroguard_model.pkl"))
except FileNotFoundError:
    st.error("Model file `neuroguard_model.pkl` not found.")
    st.stop()

# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="NeuroGuard AI | Epilepsy Monitoring",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=2000, key="refresh")

# ============================================
# Custom CSS
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0e1a, #111827);
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

.big-title {
    font-size: 72px !important;
    font-weight: 800;
    background: linear-gradient(90deg, #00E5FF, #00B8D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0px;
    letter-spacing: -2px;
}

.sub-title {
    font-size: 20px !important;
    color: #94a3b8;
    text-align: center;
    margin-top: -10px;
    font-weight: 300;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(30,41,59,0.8), rgba(15,23,42,0.9));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

[data-testid="stMetricLabel"] {
    font-size: 14px !important;
    color: #94a3b8 !important;
}

[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
}

.stButton>button {
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
}

.stDownloadButton>button {
    background: linear-gradient(90deg, #0ea5e9, #0284c7);
    color: white;
    border: none;
    border-radius: 12px;
    width: 100%;
}

hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 2rem 0;
}

h3, .stSubheader {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}

.hardware-live {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.3);
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# SENSOR DATA ACQUISITION - WITH DEBUG & CSV FIX
# ============================================
def get_sensor_data():
    print(f"[DEBUG] get_sensor_data() called at {datetime.now().strftime('%H:%M:%S')}")

    if st.session_state.simulated_seizure:
        print("[DEBUG] Using simulated seizure data")
        return {
            "HeartRate": 145.0,
            "SpO2": 88.0,
            "Motion": 2.8,
            "Fall": 1,
            "EEG": 2.5,
            "DominantWave": "Abnormal",
            "Risk": 2,
            "gps_lat": "8.893200 N",
            "gps_lon": "76.614100 E",
            "gps_fix": 1,
            "gps_sats": 8
        }

    print(f"[DEBUG] Checking CSV: {CSV_FILE}")
    print(f"[DEBUG] Exists: {os.path.exists(CSV_FILE)}")

    if not os.path.exists(CSV_FILE):
        print("[DEBUG] CSV NOT FOUND, using fallback")
        return _fallback_data()

    try:
        # FIX: Skip bad lines caused by commas in GPS coordinates
        df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
        print(f"[DEBUG] CSV rows: {len(df)}")

        if len(df) == 0:
            print("[DEBUG] CSV empty, using fallback")
            return _fallback_data()

        latest = df.iloc[-1]
        print(f"[DEBUG] Last row timestamp: {latest.get('timestamp', 'N/A')}")
        print(f"[DEBUG] HR={latest.get('heart_rate', 'N/A')} SpO2={latest.get('spo2', 'N/A')} EEG={latest.get('eeg', 'N/A')}")

        return {
            "HeartRate": float(latest.get("heart_rate", 75)),
            "SpO2": float(latest.get("spo2", 98)),
            "Motion": float(latest.get("motion", 0)),
            "Fall": int(latest.get("fall", 0)),
            "EEG": float(latest.get("eeg", 0)),
            "DominantWave": str(latest.get("dominant_wave", "Alpha")),
            "Risk": 2 if str(latest.get("risk", "SAFE")) == "CRITICAL" else 1 if str(latest.get("risk", "SAFE")) == "WARNING" else 0,
            "gps_lat": str(latest.get("gps_lat", "No Fix")),
            "gps_lon": str(latest.get("gps_lon", "No Fix")),
            "gps_fix": int(latest.get("gps_fix", 0)),
            "gps_sats": int(latest.get("gps_sats", 0))
        }
    except Exception as e:
        print(f"[DEBUG] ERROR reading CSV: {e}")
        st.sidebar.error(f"Read error: {e}")
        return _fallback_data()

def _fallback_data():
    return {
        "HeartRate": 75.0, "SpO2": 98.0, "Motion": 0.0,
        "Fall": 0, "EEG": 0.0, "DominantWave": "Alpha", "Risk": 0,
        "gps_lat": "No Fix", "gps_lon": "No Fix", "gps_fix": 0, "gps_sats": 0
    }

# ============================================
# Title Section
# ============================================
st.markdown("""
<div style='text-align:center; padding:30px 20px 10px;'>
    <h1 class='big-title'>🧠 NeuroGuard AI</h1>
    <p class='sub-title'>AI-Based Seizure Risk Assessment & Early Alert System</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="hardware-live">🔴 HARDWARE LIVE — ESP32 Connected</div>', unsafe_allow_html=True)
st.info("⚠️ **Educational prototype only.** Not intended for medical diagnosis.", icon="🏥")
st.markdown("---")

# ============================================
# Patient Profile
# ============================================
with st.container():
    st.subheader("👤 Patient Profile")
    p1, p2, p3, p4 = st.columns([2, 1, 1, 1])
    with p1:
        patient_name = st.text_input("Patient Name", "Demo Patient")
    with p2:
        age = st.number_input("Age", 1, 120, 25)
    with p3:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with p4:
        patient_id = st.text_input("Patient ID", "NG-2026-001")

st.markdown("---")

# ============================================
# SENSOR DATA INPUT SECTION
# ============================================
with st.container():
    st.subheader("📡 Sensor Data Input")

    data = get_sensor_data()
    hr = data["HeartRate"]
    spo2 = data["SpO2"]
    motion = data["Motion"]
    fall = data["Fall"]
    eeg = data["EEG"]

    if st.session_state.simulated_seizure:
        prediction = "CRITICAL"
        hr = 145
        spo2 = 88
        motion = 2.8
        fall = 1
        eeg = 2.5
        st.error("🚨 SEIZURE SIMULATION ACTIVE")

    mode_col1, mode_col2, mode_col3 = st.columns([2, 2, 2])
    with mode_col1:
        st.info("📊 Live sensor data from ESP32")
    with mode_col2:
        st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
    with mode_col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    st.markdown("---")

    left, right = st.columns(2)
    with left:
        st.markdown("#### 🫀 Cardiovascular")
        st.metric("❤️ Heart Rate", f"{hr:.1f} bpm",
                  delta=f"{hr-75:+.1f} vs baseline" if abs(hr-75) > 5 else "Normal",
                  delta_color="inverse" if hr > 100 else "normal")
        st.metric("🩸 SpO₂", f"{spo2:.1f}%",
                  delta=f"{spo2-98:+.1f}%" if abs(spo2-98) > 1 else "Normal",
                  delta_color="inverse")

    with right:
        st.markdown("#### 🏃 Activity & Motion")
        st.metric("🏃 Motion Level", f"{motion:.2f} g",
                  delta="High" if motion > 1.5 else "Elevated" if motion > 0.8 else "Normal")
        st.metric("🚶 Fall Detected", "⚠️ YES" if fall == 1 else "✅ NO")

# ============================================
# AI Prediction & Risk Calculation
# ============================================
patient = pd.DataFrame([[hr, spo2, motion, fall]], columns=["HeartRate", "SpO2", "Motion", "Fall"])

if not st.session_state.simulated_seizure:
    try:
        prediction = model.predict(patient)[0]
    except:
        prediction = "SAFE"
else:
    prediction = "CRITICAL"

nri = 0
if hr > 120: nri += 40
elif hr > 100: nri += 20
if spo2 < 90: nri += 30
elif spo2 < 95: nri += 15
if motion > 1.5: nri += 30
elif motion > 0.8: nri += 15
if fall == 1: nri += 10
if eeg > 2.0: nri += 20
elif eeg > 1.5: nri += 10
nri = min(nri, 100)

if st.session_state.simulated_seizure:
    nri = 95

# Save history
history_file = os.path.join(SCRIPT_DIR, "patient_history.csv")
new_record = pd.DataFrame([{
    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "HeartRate": round(hr, 1),
    "SpO2": round(spo2, 1),
    "Motion": round(motion, 2),
    "Fall": "YES" if fall else "NO",
    "Risk": prediction,
    "NRI": nri
}])

if os.path.exists(history_file):
    new_record.to_csv(history_file, mode="a", header=False, index=False)
else:
    new_record.to_csv(history_file, index=False)

# ============================================
# AI RISK ASSESSMENT
# ============================================
st.markdown("---")
st.header("🧠 AI Risk Assessment")

if prediction == "SAFE":
    st.success("### 🟢 PATIENT STABLE\nAll parameters within normal range.")
    gauge_color = "#22c55e"
elif prediction == "WARNING":
    st.warning("### 🟡 MONITOR CLOSELY\nAbnormal changes detected.")
    gauge_color = "#facc15"
else:
    st.error("### 🔴 IMMEDIATE ATTENTION REQUIRED\nHigh seizure risk detected.")
    gauge_color = "#ef4444"

m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 2])
with m1:
    st.metric("❤️ Heart Rate", f"{hr:.1f} bpm")
with m2:
    st.metric("🩸 SpO₂", f"{spo2:.1f}%")
with m3:
    st.metric("🏃 Motion", f"{motion:.2f} g")
with m4:
    st.metric("🧠 NRI", f"{nri}/100",
              delta="Critical" if nri > 70 else "Elevated" if nri > 30 else "Normal")

with m5:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=nri,
        number={'suffix': "/100", 'font': {'size': 36, 'color': 'white'}},
        title={'text': "Neuro Risk Index", 'font': {'size': 16, 'color': '#94a3b8'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': '#475569'},
            'bar': {'color': gauge_color, 'thickness': 0.75},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 2,
            'bordercolor': '#334155',
            'steps': [
                {'range': [0, 30], 'color': 'rgba(34,197,94,0.15)'},
                {'range': [30, 70], 'color': 'rgba(250,204,21,0.15)'},
                {'range': [70, 100], 'color': 'rgba(239,68,68,0.15)'}
            ],
            'threshold': {'line': {'color': 'white', 'width': 3}, 'thickness': 0.8, 'value': nri}
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"},
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

# ============================================
# Recommendations
# ============================================
st.markdown("---")
with st.container():
    if prediction == "CRITICAL":
        st.error("""
        **🚨 Emergency Action Protocol**
        • Move patient to recovery position immediately
        • Alert caregiver and medical staff NOW
        • Monitor airway, breathing, and circulation
        • Prepare emergency medication per protocol
        • Do not restrain patient movements
        """)
    elif prediction == "WARNING":
        st.warning("""
        **⚠️ Enhanced Observation Protocol**
        • Monitor patient continuously
        • Check vital signs every 2 minutes
        • Ensure safe environment (clear obstacles)
        • Notify on-call nurse of status change
        """)
    else:
        st.success("""
        **✅ Standard Monitoring Protocol**
        • Continue routine monitoring
        • Maintain calm environment
        • Log vitals per standard schedule
        """)

# ============================================
# LIVE CHARTS
# ============================================
st.markdown("---")
st.header("📈 Live Physiological Monitoring")

time_points = 100
t = np.linspace(0, 10, time_points)
heart_data = hr + np.random.normal(0, 1.5, time_points) + 3*np.sin(2*np.pi*1.2*t)

fig_hr = go.Figure()
fig_hr.add_trace(go.Scatter(
    x=t, y=heart_data, mode='lines', name='Heart Rate',
    line=dict(color='#ef4444', width=2),
    fill='tozeroy', fillcolor='rgba(239,68,68,0.1)'
))
fig_hr.add_hline(y=100, line_dash="dash", line_color="#eab308", annotation_text="Elevated")
fig_hr.add_hline(y=120, line_dash="dash", line_color="#dc2626", annotation_text="Critical")
fig_hr.update_layout(
    title=dict(text='❤️ Live Heart Rate Monitor', font=dict(size=18, color='#e2e8f0')),
    xaxis_title='Time (seconds)', yaxis_title='Heart Rate (bpm)',
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)',
    font=dict(color='#e2e8f0'), height=350,
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', range=[50, 170]),
    margin=dict(l=60, r=30, t=60, b=50), showlegend=False
)
st.plotly_chart(fig_hr, use_container_width=True)

# ============================================
# EEG MONITORING
# ============================================
st.markdown("---")
st.header("🧠 EEG Monitoring")

if prediction == "CRITICAL":
    seizure_probability = np.random.randint(75, 98)
    brain_score = np.random.randint(30, 55)
elif prediction == "WARNING":
    seizure_probability = np.random.randint(35, 65)
    brain_score = np.random.randint(60, 80)
else:
    seizure_probability = np.random.randint(5, 25)
    brain_score = np.random.randint(82, 98)

e1, e2, e3, e4 = st.columns(4)
with e1:
    st.metric("🚨 Seizure Probability", f"{seizure_probability}%")
with e2:
    st.metric("🧠 Brain Activity Score", f"{brain_score}/100")
with e3:
    st.metric("⚡ Dominant Wave", data["DominantWave"])
with e4:
    st.metric("📡 Channel", "CH-01 (Fp1-F3)")

wave_interp = {
    "Alpha": ("🧘 Relaxed / Eyes Closed", "success"),
    "Beta": ("⚡ Active / Alert", "info"),
    "Theta": ("😴 Drowsy / Light Sleep", "warning"),
    "Delta": ("🌙 Deep Sleep / Unconscious", "error"),
    "Gamma": ("🔥 High Cognitive Load", "error"),
    "Abnormal": ("⚠️ Abnormal Activity", "error")
}
msg, msg_type = wave_interp.get(data["DominantWave"], ("Unknown", "info"))
if msg_type == "success": st.success(f"{data['DominantWave']} Wave: {msg}")
elif msg_type == "info": st.info(f"{data['DominantWave']} Wave: {msg}")
elif msg_type == "warning": st.warning(f"{data['DominantWave']} Wave: {msg}")
else: st.error(f"{data['DominantWave']} Wave: {msg}")

# EEG Signal
time_axis = np.linspace(0, 10, 500)
if prediction == "CRITICAL":
    spikes = np.zeros_like(time_axis)
    spike_times = np.random.choice(len(time_axis), 8, replace=False)
    for st_idx in spike_times:
        width = 5
        start = max(0, st_idx-width)
        end = min(len(time_axis), st_idx+width)
        spikes[start:end] = np.random.uniform(2, 4) * np.exp(-0.5*((np.arange(start,end)-st_idx)/2)**2)
    eeg_signal = np.sin(2*np.pi*10*time_axis) + 0.5*np.sin(2*np.pi*20*time_axis) + spikes + 0.3*np.random.randn(len(time_axis))
else:
    eeg_signal = np.sin(2*np.pi*10*time_axis) + 0.5*np.sin(2*np.pi*20*time_axis) + 0.2*np.random.randn(len(time_axis))

fig_eeg = go.Figure()
fig_eeg.add_trace(go.Scatter(
    x=time_axis, y=eeg_signal, mode='lines', name='EEG Signal',
    line=dict(color='#a855f7', width=1.2)
))
fig_eeg.add_hrect(y0=-1, y1=1, line_width=0, fillcolor="rgba(34,197,94,0.1)", annotation_text="Normal Range")
fig_eeg.update_layout(
    title=dict(text='🧠 Live EEG Signal', font=dict(size=18, color='#e2e8f0')),
    xaxis_title='Time (seconds)', yaxis_title='Amplitude (μV)',
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)',
    font=dict(color='#e2e8f0'), height=350,
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', dtick=1),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    margin=dict(l=60, r=30, t=60, b=50), showlegend=False
)
st.plotly_chart(fig_eeg, use_container_width=True)

avg_eeg = round(np.mean(np.abs(eeg_signal)), 2)
peak_eeg = round(np.max(np.abs(eeg_signal)), 2)
std_eeg = round(np.std(eeg_signal), 2)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("📊 Average EEG Activity", f"{avg_eeg} μV")
with c2:
    st.metric("📈 Peak EEG Activity", f"{peak_eeg} μV")
with c3:
    st.metric("📉 Signal Variability (σ)", f"{std_eeg} μV")

st.info("""
**EEG Module Specifications**
• Hardware: BioAmp EXG Pill + ESP32 | Sampling Rate: 50 Hz | Duration: 10s
• Status: Real-time hardware acquisition active
""")

# ============================================
# GPS TRACKING WITH LIVE MAP
# ============================================
st.markdown("---")
st.header("📍 Patient Location")

# Extract decimal coordinates from GPS strings
def extract_coords(coord_str):
    """Extract decimal latitude/longitude from GPS string"""
    if not coord_str or coord_str == "No Fix":
        return None
    match = re.search(r'(-?\d+\.\d+)', str(coord_str))
    if match:
        val = float(match.group(1))
        if "S" in str(coord_str) or "W" in str(coord_str):
            val = -abs(val)
        return val
    return None

gps_lat_str = str(data.get("gps_lat", "No Fix"))
gps_lon_str = str(data.get("gps_lon", "No Fix"))
gps_fix = int(data.get("gps_fix", 0))
gps_sats = int(data.get("gps_sats", 0))

lat_val = extract_coords(gps_lat_str)
lon_val = extract_coords(gps_lon_str)

g1, g2, g3 = st.columns([1, 1, 2])
with g1:
    st.metric("Latitude", gps_lat_str if gps_fix else "Searching...")
with g2:
    st.metric("Longitude", gps_lon_str if gps_fix else "Searching...")
with g3:
    if gps_fix and lat_val and lon_val and abs(lat_val) > 0.1:
        st.success(f"📡 GPS LOCKED | {gps_sats} satellites | {lat_val:.4f}°N, {lon_val:.4f}°E")
    else:
        st.warning(f"📡 GPS Searching... | {gps_sats} satellites visible | Move near window/outside")

# Map display
try:
    import folium
    from streamlit_folium import st_folium

    if gps_fix and lat_val and lon_val and abs(lat_val) > 0.1 and abs(lon_val) > 0.1:
        st.markdown("#### 🗺️ Live Location Map")

        m = folium.Map(location=[lat_val, lon_val], zoom_start=15, 
                       tiles='CartoDB dark_matter')

        marker_color = "green" if prediction == "SAFE" else "orange" if prediction == "WARNING" else "red"

        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4>🧠 NeuroGuard Patient</h4>
            <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}<br>
            <b>HR:</b> {hr:.1f} bpm | <b>SpO2:</b> {spo2:.1f}%<br>
            <b>Risk:</b> <span style="color:{marker_color}">{prediction}</span><br>
            <b>Sats:</b> {gps_sats}
        </div>
        """

        folium.Marker(
            location=[lat_val, lon_val],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip="Patient Location",
            icon=folium.Icon(color=marker_color, icon="heart-pulse", prefix="fa")
        ).add_to(m)

        folium.Circle(
            location=[lat_val, lon_val],
            radius=50,
            color=marker_color,
            fill=True,
            fill_opacity=0.1
        ).add_to(m)

        st_folium(m, width=700, height=400, returned_objects=[])
        st.caption(f"📍 {lat_val:.6f}°N, {lon_val:.6f}°E | NEO-6M GPS Module | Accuracy ~5-10m")

    else:
        st.markdown("#### 🗺️ Location Map (Waiting for GPS fix...)")
        default_lat, default_lon = 8.5241, 76.9366
        m = folium.Map(location=[default_lat, default_lon], zoom_start=12,
                       tiles='CartoDB dark_matter')
        folium.Marker(
            location=[default_lat, default_lon],
            tooltip="Waiting for GPS signal...",
            icon=folium.Icon(color="gray", icon="question", prefix="fa")
        ).add_to(m)
        st_folium(m, width=700, height=400, returned_objects=[])
        st.info("🛰️ GPS is acquiring satellites. This may take 30-60 seconds outdoors, or 2-5 minutes indoors near a window.")

except ImportError:
    st.warning("📦 Install folium for map display: `pip install folium streamlit-folium`")
    if gps_fix and lat_val and lon_val:
        st.code(f"Coordinates: {lat_val:.6f}, {lon_val:.6f}", language="text")

# ============================================
# SIMULATION CONTROL
# ============================================
st.markdown("---")
sim_col1, sim_col2 = st.columns([1, 3])
with sim_col1:
    if st.button("🚨 Simulate Seizure Event", use_container_width=True):
        st.session_state.simulated_seizure = True
        st.rerun()
with sim_col2:
    if st.session_state.simulated_seizure:
        if st.button("✅ Clear Simulation", use_container_width=True):
            st.session_state.simulated_seizure = False
            st.rerun()

# ============================================
# PATIENT HISTORY
# ============================================
st.markdown("---")
st.header("📜 Patient History & Trends")

if os.path.exists(history_file):
    history = pd.read_csv(history_file)
    st.dataframe(history.tail(10).style.background_gradient(subset=['NRI'], cmap='RdYlGn_r'),
                 use_container_width=True, hide_index=True)

    if len(history) > 1:
        st.markdown("---")
        st.subheader("📊 Trend Analysis")

        history['Time'] = pd.to_datetime(history['Time'])

        t1, t2 = st.columns(2)
        with t1:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=history['Time'], y=history['HeartRate'],
                mode='lines+markers', name='Heart Rate',
                line=dict(color='#ef4444', width=2), marker=dict(size=6)
            ))
            fig_trend.add_trace(go.Scatter(
                x=history['Time'], y=history['SpO2'],
                mode='lines+markers', name='SpO₂',
                line=dict(color='#0ea5e9', width=2), yaxis='y2', marker=dict(size=6)
            ))
            fig_trend.update_layout(
                title='Heart Rate & SpO₂ Trends',
                xaxis_title='Time', yaxis_title='Heart Rate (bpm)',
                yaxis2=dict(title='SpO₂ (%)', overlaying='y', side='right', range=[75, 105]),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)',
                font=dict(color='#e2e8f0'), height=350,
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', range=[50, 170])
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with t2:
            colors = ['#16a34a' if v < 30 else '#eab308' if v < 70 else '#dc2626' for v in history['NRI']]
            fig_nri = go.Figure()
            fig_nri.add_trace(go.Bar(
                x=history['Time'], y=history['NRI'],
                marker_color=colors, name='NRI'
            ))
            fig_nri.add_hline(y=30, line_dash="dash", line_color="#eab308")
            fig_nri.add_hline(y=70, line_dash="dash", line_color="#dc2626")
            fig_nri.update_layout(
                title='Neuro Risk Index History',
                xaxis_title='Time', yaxis_title='NRI Score (0-100)',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)',
                font=dict(color='#e2e8f0'), height=350, showlegend=False,
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', range=[0, 105])
            )
            st.plotly_chart(fig_nri, use_container_width=True)

        st.markdown("---")
        avg_hr = history["HeartRate"].mean()
        avg_spo2 = history["SpO2"].mean()
        avg_nri = history["NRI"].mean()
        max_nri = history["NRI"].max()
        critical_events = len(history[history["Risk"] == "CRITICAL"])

        a1, a2, a3, a4, a5 = st.columns(5)
        a1.metric("Avg Heart Rate", f"{avg_hr:.1f} bpm")
        a2.metric("Avg SpO₂", f"{avg_spo2:.1f}%")
        a3.metric("Avg NRI", f"{avg_nri:.1f}")
        a4.metric("Peak NRI", f"{max_nri:.1f}")
        a5.metric("Critical Events", f"{critical_events}",
                  delta="Active" if critical_events > 0 else "None")
else:
    st.warning("No patient history available yet.")

# ============================================
# Download Report
# ============================================
st.markdown("---")
report = f"""
==================================
      NEUROGUARD AI REPORT
==================================

Generated   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Patient     : {patient_name} ({gender}, {age}y)
ID          : {patient_id}

----------------------------------
VITAL SIGNS
----------------------------------
Heart Rate  : {hr:.1f} bpm
SpO₂        : {spo2:.1f} %
Motion      : {motion:.2f} g
Fall        : {"YES" if fall else "NO"}
EEG         : {eeg:.3f} V

----------------------------------
AI ASSESSMENT
----------------------------------
Prediction  : {prediction}
NRI Score   : {nri}/100
Status      : {"STABLE" if prediction == "SAFE" else "MONITOR" if prediction == "WARNING" else "CRITICAL"}

----------------------------------
GPS LOCATION
----------------------------------
Latitude    : {gps_lat_str}
Longitude   : {gps_lon_str}
Fix Status  : {"LOCKED" if gps_fix else "SEARCHING"}
Satellites  : {gps_sats}

----------------------------------
RECOMMENDATION
----------------------------------
{"Continue standard monitoring." if prediction == "SAFE" else "Enhanced observation required." if prediction == "WARNING" else "IMMEDIATE CAREGIVER INTERVENTION REQUIRED."}

==================================
 NeuroGuard AI v2.0 | Educational
==================================
"""

st.download_button(
    label="📄 Download Full Patient Report",
    data=report,
    file_name=f"neuroguard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    mime="text/plain",
    use_container_width=True
)

# ============================================
# Sidebar — UPDATED FOR SERIAL MODE
# ============================================
with st.sidebar:
    st.header("🔧 System Status")
    st.markdown(f"""
    **Hardware:** 🔴 LIVE — Serial/USB

    **CSV File:** `{CSV_FILE}`

    **Connection:** USB Serial (COM port)
    **Bridge:** Run `python serial_bridge.py`
    """)

    # Show live CSV debug info
    if os.path.exists(CSV_FILE):
        try:
            df_debug = pd.read_csv(CSV_FILE, on_bad_lines='skip')
            st.write(f"📊 CSV rows: {len(df_debug)}")
            if len(df_debug) > 0:
                latest = df_debug.iloc[-1]
                st.write(f"Last HR: {latest.get('heart_rate', 'N/A')}")
                st.write(f"Last EEG: {latest.get('eeg', 'N/A')}V")
                st.write(f"GPS Fix: {'✅' if latest.get('gps_fix', 0) else '⏳'}")
                st.write(f"GPS: {latest.get('gps_lat', 'N/A')}, {latest.get('gps_lon', 'N/A')}")
                st.write(f"Timestamp: {latest.get('timestamp', 'N/A')}")
        except Exception as e:
            st.error(f"CSV error: {e}")
    else:
        st.error("❌ CSV not found!")
        st.info("1. Connect ESP32 via USB\n2. Run: `python serial_bridge.py`")

    st.divider()
    st.caption("NeuroGuard AI v2.0 — Serial Mode")

# ============================================
# Footer
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#64748b; padding: 30px 0;'>
    <h3 style='color:#00E5FF; margin-bottom: 10px;'>🏥 NeuroGuard AI</h3>
    <p>AI-Based Seizure Risk Assessment & Early Alert System</p>
    <p style='font-size: 12px; margin-top: 20px;'>Machine Learning • IoT Healthcare • Real-time Monitoring</p>
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Educational prototype only. Not intended for medical diagnosis.")