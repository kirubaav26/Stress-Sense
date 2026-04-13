import streamlit as st
import pandas as pd
import joblib
import networkx as nx
import matplotlib.pyplot as plt
import random

# --- CONFIG & CYBER-HUD STYLING ---
st.set_page_config(page_title="SCI Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at top, #1b2735 0%, #090a0f 100%);
        color: #e0e0e0;
    }

    /* Glassmorphism Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(30, 33, 48, 0.4);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 15px;
        backdrop-filter: blur(12px);
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    /* Neon Titles */
    h1, h2 {
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Form and Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid #1b2735;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #0055ff);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- MODEL LOADING ---
try:
    model = joblib.load('stress_model.pkl')
except Exception as e:
    st.error(f"Model file 'stress_model.pkl' not found. Error: {e}")
    st.stop()

# --- DIALOG DEFINITION ---
@st.dialog("🚨 SYSTEM OVERRIDE: STRESS DETECTED")
def trigger_intervention(level, suggestions, hr):
    st.markdown(f"<h2 style='color:#ff3131;'>{level}</h2>", unsafe_allow_html=True)
    st.write(f"Physiological state exceeds safety buffer at **{hr} BPM**.")
    st.divider()
    st.markdown("What You Can Do")
    selected_tips = random.sample(suggestions, 3)
    for tip in selected_tips:
        st.markdown(f"🔹 {tip}")
    st.info("System Lockdown: Monitoring will resume once vitals stabilize.")

# --- SIDEBAR & FORM ---
with st.sidebar:
    st.header("INPUTS")
    with st.form("input_form"):
        anxiety = st.slider("Anxiety (GAD-7)", 0, 21, 5)
        sleep = st.slider("Sleep Quality (0-5)", 0, 5, 4)
        load = st.slider("Workload (0-5)", 0, 5, 2)
        current_hr = st.slider("Live Pulse (BPM)", 60, 140, 75)
        submitted = st.form_submit_button("SUBMIT")

st.title("🛡️ Stress Cascade Interrupter")
st.markdown("#### *Real-Time Predictive Bio-Feedback Engine*")
st.write("---")

if submitted:
    # 1. Calculations
    input_df = pd.DataFrame([[anxiety, sleep, load]], columns=['anxiety_level', 'sleep_quality', 'study_load'])
    probs = model.predict_proba(input_df)[0]
    stress_prob = probs[-1]

    # 2. High-Sensitivity Logic
    base_threshold = 100
    anx_penalty = (anxiety / 21) * 25
    slp_penalty = ((5 - sleep) / 5) * 25
    ml_penalty = stress_prob * 30
    dynamic_threshold = base_threshold - (anx_penalty + slp_penalty + ml_penalty)

    # 3. HUD Metrics
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Predictive Risk", f"{stress_prob*100:.1f}%")
    with m2: st.metric("Dynamic Limit", f"{dynamic_threshold:.1f} BPM", f"-{base_threshold-dynamic_threshold:.1f}", delta_color="inverse")
    with m3: st.metric("Current Pulse", f"{current_hr} BPM")

    st.write("---")

    # 4. Intervention Logic
    if current_hr > dynamic_threshold:
        norm_anx, norm_slp, norm_lod = anxiety/21, (5-sleep)/5, load/5
        if norm_anx >= norm_slp and norm_anx >= norm_lod:
            level, pool = "Anxiety Spike", [
                "Practice Box Breathing: 4s In, 4s Hold, 4s Out.",
                "Splash ice-cold water on your face.",
                "5-4-3-2-1 Grounding: Name 5 things you see.",
                "Unclench jaw and drop your shoulders.",
                "Listen to Brown Noise for 2 minutes."
            ]
        elif norm_slp >= norm_anx and norm_slp >= norm_lod:
            level, pool = "Sleep Crisis", [
                "Immediate 20-minute power nap required.",
                "Drink 500ml of cold water.",
                "Step into direct sunlight/bright light.",
                "10 jumping jacks to boost circulation.",
                "Wash face with cold water."
            ]
        else:
            level, pool = "Cognitive Overload", [
                "Initiate Pomodoro: 25m focus / 5m break.",
                "Close all unnecessary browser tabs.",
                "Break current task into 3 micro-steps.",
                "Stand up and walk away from desk for 5 mins.",
                "Prioritize the single most important task."
            ]
        trigger_intervention(level, pool, current_hr)
    else:
        st.success("✅ BIOMETRICS STABLE: WITHIN OPERATIONAL LIMITS")

    # 5. Visualizer
    st.subheader("🕸️ Stressor Synergy Network")
    G = nx.DiGraph()
    G.add_edge("Anxiety", "STRESS", weight=(anxiety/21)*10)
    G.add_edge("Sleep", "STRESS", weight=(5-sleep)*4)
    G.add_edge("Workload", "STRESS", weight=load*2)
    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    pos = {"Anxiety": (0, 1), "Sleep": (0, 0), "Workload": (0, -1), "STRESS": (1.2, 0)}
    nx.draw(G, pos, with_labels=True, node_color='#00d4ff', node_size=3000, font_weight='bold', font_color='white', edge_color='#ff3131', arrows=True, arrowsize=20)
    st.pyplot(fig)
else:
    st.info("Adjust sliders and initialize scan.")