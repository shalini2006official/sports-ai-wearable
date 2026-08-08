import streamlit as st
import random
import time
import math
import plotly.graph_objects as go
import plotly.express as px
import json
import hashlib

st.set_page_config(
    page_title="Sports AI Wearable",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── User Database ────────────────────────────────────────────
USERS = {
    "players": {
        "shalini": {"password": hashlib.md5("player123".encode()).hexdigest(), "name": "Shalini", "sport": "Cricket",  "max_hr": 190, "age": 22, "jersey": "#7"},
        "rahul":   {"password": hashlib.md5("player123".encode()).hexdigest(), "name": "Rahul",   "sport": "Football", "max_hr": 185, "age": 24, "jersey": "#10"},
        "priya":   {"password": hashlib.md5("player123".encode()).hexdigest(), "name": "Priya",   "sport": "Badminton","max_hr": 188, "age": 21, "jersey": "#3"},
    },
    "coaches": {
        "coach1": {"password": hashlib.md5("coach123".encode()).hexdigest(), "name": "Coach Kumar", "team": "Team Alpha"},
        "coach2": {"password": hashlib.md5("coach123".encode()).hexdigest(), "name": "Coach Meena", "team": "Team Beta"},
    }
}

# ─── AI Coaching ──────────────────────────────────────────────
def analyze_performance(heart_rate, total_steps, activity, max_hr=190, spo2=98, temp=36.5):
    hr_zone = (heart_rate / max_hr) * 100
    advice = []
    alert_level = "green"

    if hr_zone > 90:
        advice.append("🚨 DANGER: Heart rate critically high! Stop and rest immediately.")
        alert_level = "red"
    elif hr_zone > 75:
        advice.append("⚠️ HIGH INTENSITY: You're pushing hard! Monitor your breathing.")
        alert_level = "orange"
    elif hr_zone > 50:
        advice.append("✅ OPTIMAL ZONE: Perfect training intensity! Keep it up.")
        alert_level = "green"
    else:
        advice.append("💤 LOW INTENSITY: Heart rate is low. You can push harder!")
        alert_level = "blue"

    if spo2 < 95:
        advice.append("🫀 SpO2 dropping! Rest and breathe deeply.")
        alert_level = "red"
    if temp > 37.5:
        advice.append("🌡️ Body temperature elevated — risk of heat exhaustion!")
    if activity == "Running" and heart_rate > 160:
        advice.append("🏃 Slow your running pace to avoid overexertion.")
    elif activity == "Resting" and heart_rate > 100:
        advice.append("😴 Heart rate high at rest — take a longer break.")
    elif activity == "Jumping":
        advice.append("⬆️ High-impact activity — land softly to protect joints.")
    if total_steps > 500:
        advice.append(f"👟 {total_steps:,} steps done — stay hydrated!")

    return advice, round(hr_zone, 1), alert_level

# ─── Simulate Sensors ─────────────────────────────────────────
def simulate_wrist():
    ax = round(random.uniform(-2.0, 2.0), 2)
    ay = round(random.uniform(-2.0, 2.0), 2)
    az = round(random.uniform(-2.0, 2.0), 2)
    mag = math.sqrt(ax**2 + ay**2 + az**2)
    act = "Jumping" if mag>2.5 else ("Running" if mag>1.8 else ("Walking" if mag>1.2 else "Resting"))
    return {"heart_rate": random.randint(60,180), "spo2": random.randint(95,100),
            "steps": random.randint(0,5), "accel_x":ax, "accel_y":ay, "accel_z":az,
            "activity":act, "temperature":round(random.uniform(36.0,37.5),1)}

def simulate_waist():
    ax=round(random.uniform(-1.5,1.5),2); ay=round(random.uniform(-1.5,1.5),2); az=round(random.uniform(-1.5,1.5),2)
    tilt=round(math.degrees(math.atan2(math.sqrt(ax**2+ay**2),abs(az))),1)
    return {"accel_x":ax,"accel_y":ay,"accel_z":az,"spine_tilt":tilt,
            "posture":"Good" if tilt<15 else ("Fair" if tilt<30 else "Bad")}

def simulate_ankle():
    ax=round(random.uniform(-2.5,2.5),2); ay=round(random.uniform(-2.5,2.5),2); az=round(random.uniform(-2.5,2.5),2)
    mag=math.sqrt(ax**2+ay**2+az**2)
    return {"accel_x":ax,"accel_y":ay,"accel_z":az,"steps":random.randint(0,3),
            "stride_length":round(random.uniform(0.4,0.9),2) if mag>1.5 else 0.0,
            "cadence":random.randint(0,5)}

def read_sensor(filepath, sim_fn):
    try:
        with open(filepath,"r") as f: return json.load(f), True
    except: return sim_fn(), False

# ─── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');
*,html,body,[class*="css"]{font-family:'Inter',sans-serif;box-sizing:border-box;}
.main{background:#0b0f19!important;}
.block-container{padding:0!important;max-width:100%!important;}

@keyframes pulse     {0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.3;transform:scale(0.75)}}
@keyframes fadeUp    {from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideLeft {from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}}
@keyframes heartbeat {0%,100%{transform:scale(1)}15%{transform:scale(1.3)}30%{transform:scale(1)}45%{transform:scale(1.15)}}
@keyframes float     {0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@keyframes zoneGrow  {from{width:0}}
@keyframes borderAnim{0%{background-position:0% 50%}100%{background-position:200% 50%}}
@keyframes glow      {0%,100%{opacity:0.5}50%{opacity:1}}
@keyframes gradMove  {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

/* ── LOGIN PAGE ── */
.login-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0d1422 100%);
    display: flex; align-items: center; justify-content: center;
    padding: 2rem;
}
.login-container {
    width: 100%; max-width: 420px;
    background: #111827;
    border-radius: 24px;
    border: 1px solid #1e293b;
    padding: 40px 36px;
    animation: fadeUp 0.6s ease-out;
    box-shadow: 0 24px 64px rgba(0,0,0,0.4);
    margin: 0 auto;
}
.login-logo {
    text-align: center; margin-bottom: 28px;
}
.login-logo-icon {
    font-size: 3em;
    display: block;
    animation: float 3s ease-in-out infinite;
}
.login-title {
    font-family:'Rajdhani',sans-serif;
    font-size:1.8em; font-weight:700;
    background:linear-gradient(135deg,#a5b4fc,#c084fc,#f9a8d4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    letter-spacing:2px; margin-top:8px;
}
.login-sub {
    color:#475569; font-size:0.8em;
    letter-spacing:1.5px; text-transform:uppercase;
    margin-top:4px;
}
.role-tabs {
    display:grid; grid-template-columns:1fr 1fr;
    gap:8px; margin-bottom:24px;
}
.role-tab {
    padding:10px; border-radius:12px; text-align:center;
    font-size:0.85em; font-weight:600; cursor:pointer;
    border:1px solid transparent; transition:all 0.2s;
}
.role-tab.player {
    background:rgba(99,102,241,0.1); border-color:rgba(99,102,241,0.3);
    color:#a5b4fc;
}
.role-tab.coach {
    background:rgba(236,72,153,0.1); border-color:rgba(236,72,153,0.3);
    color:#f9a8d4;
}
.role-tab.active-player {
    background:rgba(99,102,241,0.25); border-color:#6366f1;
    color:#a5b4fc; box-shadow:0 0 16px rgba(99,102,241,0.3);
}
.role-tab.active-coach {
    background:rgba(236,72,153,0.25); border-color:#ec4899;
    color:#f9a8d4; box-shadow:0 0 16px rgba(236,72,153,0.3);
}
.demo-hint {
    background:rgba(255,255,255,0.03); border:1px solid #1e293b;
    border-radius:12px; padding:12px 14px; margin-bottom:20px;
    font-size:0.78em; color:#475569; line-height:1.8;
}
.demo-hint strong { color:#64748b; }

/* ── HEADER ── */
.dash-header {
    background:#111827; border-bottom:1px solid #1e293b;
    padding:14px 28px;
    display:flex; align-items:center; justify-content:space-between;
    position:sticky; top:0; z-index:100;
}
.dash-header-left { display:flex; align-items:center; gap:14px; }
.dash-logo { font-family:'Rajdhani',sans-serif; font-size:1.3em; font-weight:700; }
.dash-logo span {
    background:linear-gradient(135deg,#a5b4fc,#c084fc);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.dash-header-right { display:flex; align-items:center; gap:12px; }
.user-chip {
    display:flex; align-items:center; gap:8px;
    background:rgba(255,255,255,0.05); border:1px solid #1e293b;
    border-radius:20px; padding:6px 14px; font-size:0.82em; color:#94a3b8;
}
.user-role-badge {
    padding:3px 10px; border-radius:20px;
    font-size:0.72em; font-weight:700; letter-spacing:1px;
}
.badge-player { background:rgba(99,102,241,0.2); border:1px solid rgba(99,102,241,0.4); color:#a5b4fc; }
.badge-coach  { background:rgba(236,72,153,0.2); border:1px solid rgba(236,72,153,0.4); color:#f9a8d4; }
.live-dot { width:7px;height:7px;border-radius:50%;background:#4ade80;animation:pulse 1.5s ease-in-out infinite;display:inline-block; }

/* ── DASHBOARD BODY ── */
.dash-body { padding:24px 28px; }

/* ── PLAYER SELECTOR (coach view) ── */
.player-selector {
    display:grid; grid-template-columns:repeat(3,1fr);
    gap:10px; margin-bottom:20px;
}
.player-card-sel {
    background:#111827; border-radius:14px;
    border:1px solid #1e293b; padding:14px 16px;
    cursor:pointer; transition:all 0.2s; text-align:center;
    animation:fadeUp 0.4s ease-out;
}
.player-card-sel:hover { border-color:#6366f1; transform:translateY(-2px); }
.player-card-sel.selected { border-color:#6366f1; background:rgba(99,102,241,0.1); box-shadow:0 0 16px rgba(99,102,241,0.15); }
.pcs-name { font-family:'Rajdhani',sans-serif; font-size:1em; font-weight:700; color:#e2e8f0; }
.pcs-sport { font-size:0.75em; color:#475569; margin-top:3px; }
.pcs-status { font-size:0.72em; margin-top:6px; }
.pcs-online { color:#4ade80; } .pcs-offline { color:#334155; }

/* ── DEVICE CARDS ── */
.device-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:20px; }
.device-card { border-radius:16px; padding:14px 16px; display:flex; align-items:center; gap:12px; border:1px solid transparent; animation:fadeUp 0.5s ease-out; }
.device-card.wrist { background:linear-gradient(145deg,#1a0f2e,#2a1545); border-color:rgba(139,92,246,0.25); }
.device-card.waist { background:linear-gradient(145deg,#0f1a2d,#152845); border-color:rgba(59,130,246,0.25); }
.device-card.ankle { background:linear-gradient(145deg,#0f2d1a,#154528); border-color:rgba(34,197,94,0.25); }
.device-name { font-family:'Rajdhani',sans-serif; font-size:0.88em; font-weight:700; letter-spacing:1px; }
.device-card.wrist .device-name{color:#c4b5fd;} .device-card.waist .device-name{color:#93c5fd;} .device-card.ankle .device-name{color:#86efac;}
.device-info { font-size:0.7em; color:#334155; margin-top:3px; }
.device-badge { margin-left:auto; padding:3px 10px; border-radius:20px; font-size:0.68em; font-weight:700; letter-spacing:1px; }
.device-badge.sim  { background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3); color:#fbbf24; }
.device-badge.real { background:rgba(34,197,94,0.1);  border:1px solid rgba(34,197,94,0.3);  color:#4ade80; }

/* ── POSTURE ── */
.posture-wrap { border-radius:18px; padding:18px 24px; display:grid; grid-template-columns:1fr auto; align-items:center; gap:16px; margin-bottom:20px; animation:slideLeft 0.5s ease-out; border:1px solid transparent; }
.posture-wrap.good{background:linear-gradient(135deg,#052e16,#064e3b);border-color:rgba(34,197,94,0.25);}
.posture-wrap.fair{background:linear-gradient(135deg,#431407,#4d2207);border-color:rgba(249,115,22,0.25);}
.posture-wrap.bad {background:linear-gradient(135deg,#450a0a,#4d1212);border-color:rgba(239,68,68,0.25);}
.posture-wrap.none{background:linear-gradient(135deg,#0f172a,#111827);border-color:rgba(99,102,241,0.2);}
.posture-title{font-size:1em;font-weight:700;}
.posture-title.good{color:#4ade80;}.posture-title.fair{color:#fb923c;}.posture-title.bad{color:#f87171;}.posture-title.none{color:#818cf8;}
.posture-time{font-size:0.75em;color:#475569;margin-top:4px;}
.angle-group{display:flex;gap:10px;flex-wrap:wrap;}
.angle-chip{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:8px 18px;text-align:center;min-width:72px;}
.angle-num{font-family:'Rajdhani',sans-serif;font-size:1.3em;font-weight:700;color:#e2e8f0;}
.angle-tag{font-size:0.62em;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;}

/* ── METRICS ── */
.sec-label{font-family:'Rajdhani',sans-serif;font-size:0.78em;font-weight:600;color:#6366f1;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid #1e293b;padding-bottom:8px;margin-bottom:14px;}
.metric-card{border-radius:18px;padding:22px 18px 18px;text-align:center;position:relative;overflow:hidden;animation:fadeUp 0.5s ease-out;transition:transform 0.25s,box-shadow 0.25s;border:1px solid transparent;}
.metric-card:hover{transform:translateY(-5px);}
.metric-card.hr   {background:linear-gradient(145deg,#1a0f0f,#2d1515);border-color:rgba(239,68,68,0.2);box-shadow:0 4px 24px rgba(239,68,68,0.08);}
.metric-card.spo  {background:linear-gradient(145deg,#0f1a0f,#152815);border-color:rgba(34,197,94,0.2);box-shadow:0 4px 24px rgba(34,197,94,0.08);}
.metric-card.steps{background:linear-gradient(145deg,#0f1a2d,#152845);border-color:rgba(59,130,246,0.2);box-shadow:0 4px 24px rgba(59,130,246,0.08);}
.metric-card.act  {background:linear-gradient(145deg,#160f2d,#221545);border-color:rgba(139,92,246,0.2);box-shadow:0 4px 24px rgba(139,92,246,0.08);}
.metric-card.cal  {background:linear-gradient(145deg,#1a120a,#2d1e0f);border-color:rgba(251,146,60,0.2);box-shadow:0 4px 24px rgba(251,146,60,0.08);}
.metric-card.tmp  {background:linear-gradient(145deg,#1a0f1a,#2d1530);border-color:rgba(244,114,182,0.2);box-shadow:0 4px 24px rgba(244,114,182,0.08);}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;border-radius:18px 18px 0 0;}
.metric-card.hr::before   {background:linear-gradient(90deg,#ef4444,#f87171);}
.metric-card.spo::before  {background:linear-gradient(90deg,#22c55e,#4ade80);}
.metric-card.steps::before{background:linear-gradient(90deg,#3b82f6,#60a5fa);}
.metric-card.act::before  {background:linear-gradient(90deg,#8b5cf6,#a78bfa);}
.metric-card.cal::before  {background:linear-gradient(90deg,#f97316,#fb923c);}
.metric-card.tmp::before  {background:linear-gradient(90deg,#ec4899,#f472b6);}
.metric-icon{font-size:1.7em;display:block;margin-bottom:8px;}
.metric-icon.hb{animation:heartbeat 1.5s ease-in-out infinite;display:inline-block;}
.metric-icon.fl{animation:float 2.8s ease-in-out infinite;display:inline-block;}
.metric-val{font-family:'Rajdhani',sans-serif;font-size:2.2em;font-weight:700;letter-spacing:1px;line-height:1;}
.metric-card.hr    .metric-val{color:#fca5a5;}.metric-card.spo  .metric-val{color:#86efac;}
.metric-card.steps .metric-val{color:#93c5fd;}.metric-card.act  .metric-val{color:#c4b5fd;}
.metric-card.cal   .metric-val{color:#fdba74;}.metric-card.tmp  .metric-val{color:#f9a8d4;}
.metric-lbl{font-size:0.68em;color:#475569;text-transform:uppercase;letter-spacing:2px;margin-top:6px;}
.metric-sub{font-size:0.68em;color:#334155;margin-top:3px;}
.metric-bg{position:absolute;right:8px;bottom:4px;font-size:4em;opacity:0.04;pointer-events:none;animation:float 4s ease-in-out infinite;}

/* ── COACH & STATS ── */
.coach-wrap{background:linear-gradient(145deg,#0d1526,#111e35);border-radius:18px;border:1px solid rgba(99,102,241,0.2);padding:20px;animation:fadeUp 0.5s ease-out;}
.coach-tip{display:flex;align-items:flex-start;gap:10px;font-size:0.87em;line-height:1.6;padding:10px 14px;border-radius:10px;margin-bottom:8px;animation:slideLeft 0.4s ease-out;}
.coach-tip:last-child{margin-bottom:0;}
.coach-tip.red   {background:rgba(239,68,68,0.08);  color:#fca5a5;border-left:3px solid #ef4444;}
.coach-tip.green {background:rgba(34,197,94,0.08);  color:#86efac;border-left:3px solid #22c55e;}
.coach-tip.orange{background:rgba(249,115,22,0.08); color:#fdba74;border-left:3px solid #f97316;}
.coach-tip.blue  {background:rgba(99,102,241,0.08); color:#a5b4fc;border-left:3px solid #6366f1;}
.stats-wrap{background:#111827;border-radius:18px;border:1px solid #1e293b;padding:20px;animation:fadeUp 0.5s ease-out;}
.stat-row{display:grid;grid-template-columns:1fr auto;padding:9px 0;border-bottom:1px solid #0f172a;font-size:0.85em;}
.stat-row:last-child{border-bottom:none;}
.stat-key{color:#475569;} .stat-val{color:#e2e8f0;font-weight:600;text-align:right;}

/* ── ZONE ── */
.zone-wrap{background:#111827;border-radius:18px;border:1px solid #1e293b;padding:20px;animation:fadeUp 0.5s ease-out;}
.zone-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.zone-scale{display:flex;justify-content:space-between;font-size:0.68em;color:#334155;margin-bottom:6px;}
.zone-track{background:#0f172a;border-radius:8px;height:16px;overflow:hidden;border:1px solid #1e293b;}
.zone-fill{height:100%;border-radius:8px;animation:zoneGrow 1s ease-out;transition:width 1s ease-out,background 0.5s;}
.zone-pills{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px;}
.zone-pill{padding:6px 8px;border-radius:10px;font-size:0.72em;font-weight:600;text-align:center;border:1px solid transparent;}
.zp-off    {background:rgba(255,255,255,0.02);border-color:rgba(255,255,255,0.06);color:#334155;}
.zp-rest   {background:rgba(99,102,241,0.2);  border-color:#6366f1;color:#a5b4fc;box-shadow:0 0 10px rgba(99,102,241,0.2);}
.zp-mod    {background:rgba(34,197,94,0.2);   border-color:#22c55e;color:#86efac;box-shadow:0 0 10px rgba(34,197,94,0.2);}
.zp-high   {background:rgba(249,115,22,0.2);  border-color:#f97316;color:#fdba74;box-shadow:0 0 10px rgba(249,115,22,0.2);}
.zp-danger {background:rgba(239,68,68,0.2);   border-color:#ef4444;color:#fca5a5;box-shadow:0 0 10px rgba(239,68,68,0.2);}

/* ── WAIST/ANKLE CARDS ── */
.waist-card{background:linear-gradient(145deg,#0f1a2d,#152845);border-radius:18px;border:1px solid rgba(59,130,246,0.2);padding:20px;}
.ankle-card{background:linear-gradient(145deg,#0f2d1a,#154528);border-radius:18px;border:1px solid rgba(34,197,94,0.2);padding:20px;}
.sensor-title{font-family:'Rajdhani',sans-serif;font-size:0.82em;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;}
.waist-card .sensor-title{color:#60a5fa;} .ankle-card .sensor-title{color:#4ade80;}
.sensor-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.85em;}
.sensor-row:last-child{border-bottom:none;}
.sensor-key{color:#334155;} .sensor-val{font-weight:600;}
.waist-card .sensor-val{color:#93c5fd;} .ankle-card .sensor-val{color:#86efac;}

/* ── HISTORY ── */
.history-wrap{background:#111827;border-radius:18px;border:1px solid #1e293b;padding:20px;animation:fadeUp 0.5s ease-out;}
.history-item{display:grid;grid-template-columns:1fr auto;align-items:center;gap:12px;padding:13px 0;border-bottom:1px solid #0f172a;}
.history-item:last-child{border-bottom:none;}
.hist-date{font-size:0.85em;font-weight:700;color:#818cf8;}
.hist-meta{font-size:0.73em;color:#334155;margin-top:3px;line-height:1.6;}
.hist-stats{display:flex;gap:20px;}
.hst{text-align:center;}
.hst-val{font-family:'Rajdhani',sans-serif;font-size:1.15em;font-weight:700;}
.hst-lbl{font-size:0.62em;color:#334155;text-transform:uppercase;letter-spacing:1px;}
.no-data{text-align:center;padding:20px;color:#1e293b;font-size:0.85em;}

/* ── COACH ALERT BANNER ── */
.alert-banner{border-radius:14px;padding:14px 18px;margin-bottom:16px;animation:slideLeft 0.4s ease-out;border:1px solid transparent;}
.alert-banner.danger{background:rgba(239,68,68,0.1);border-color:rgba(239,68,68,0.3);color:#fca5a5;}
.alert-banner.warning{background:rgba(249,115,22,0.1);border-color:rgba(249,115,22,0.3);color:#fdba74;}
.alert-banner.good{background:rgba(34,197,94,0.1);border-color:rgba(34,197,94,0.3);color:#86efac;}
.alert-title{font-weight:700;font-size:0.9em;margin-bottom:4px;}
.alert-body{font-size:0.82em;opacity:0.85;}

/* ── COACH PLAYER OVERVIEW ── */
.player-overview-card{background:#111827;border-radius:16px;border:1px solid #1e293b;padding:16px;animation:fadeUp 0.4s ease-out;transition:border-color 0.2s;}
.player-overview-card:hover{border-color:#334155;}
.poc-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}
.poc-name{font-family:'Rajdhani',sans-serif;font-size:1em;font-weight:700;color:#e2e8f0;}
.poc-sport{font-size:0.72em;color:#475569;}
.poc-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.poc-stat{text-align:center;background:#0f172a;border-radius:10px;padding:8px 4px;}
.poc-val{font-family:'Rajdhani',sans-serif;font-size:1.1em;font-weight:700;}
.poc-lbl{font-size:0.62em;color:#334155;text-transform:uppercase;letter-spacing:1px;}
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────
if "logged_in"    not in st.session_state: st.session_state.logged_in = False
if "role"         not in st.session_state: st.session_state.role = None
if "username"     not in st.session_state: st.session_state.username = None
if "user_data"    not in st.session_state: st.session_state.user_data = {}
if "login_role"   not in st.session_state: st.session_state.login_role = "player"
if "sel_player"   not in st.session_state: st.session_state.sel_player = "shalini"

# ─── LOGIN PAGE ───────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div style="min-height:100vh;background:linear-gradient(135deg,#0b0f19,#111827,#0d1422);
                display:flex;align-items:center;justify-content:center;padding:2rem;">
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;margin-bottom:24px;">
            <span style="font-size:3.5em;animation:float 3s ease-in-out infinite;display:inline-block;">⚡</span>
            <div style="font-family:Rajdhani,sans-serif;font-size:1.9em;font-weight:700;
                        background:linear-gradient(135deg,#a5b4fc,#c084fc,#f9a8d4);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        letter-spacing:2px;margin-top:8px;">SPORTS AI WEARABLE</div>
            <div style="color:#334155;font-size:0.78em;letter-spacing:2px;text-transform:uppercase;margin-top:4px;">
                Performance Monitoring System
            </div>
        </div>""", unsafe_allow_html=True)

        # Role selector
        st.markdown('<div style="margin-bottom:6px;font-size:0.8em;color:#475569;text-transform:uppercase;letter-spacing:1.5px;">Login as</div>', unsafe_allow_html=True)

        role_col1, role_col2 = st.columns(2)
        with role_col1:
            if st.button("🏃 Player", use_container_width=True,
                type="primary" if st.session_state.login_role=="player" else "secondary"):
                st.session_state.login_role = "player"
                st.rerun()
        with role_col2:
            if st.button("🎯 Coach", use_container_width=True,
                type="primary" if st.session_state.login_role=="coach" else "secondary"):
                st.session_state.login_role = "coach"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Demo credentials hint
        if st.session_state.login_role == "player":
            st.markdown("""
            <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                        border-radius:12px;padding:12px 14px;margin-bottom:16px;font-size:0.78em;color:#64748b;line-height:1.9;">
                <strong style="color:#818cf8;">Demo Player Accounts:</strong><br>
                👤 shalini / player123 &nbsp;·&nbsp; Cricket<br>
                👤 rahul / player123 &nbsp;·&nbsp; Football<br>
                👤 priya / player123 &nbsp;·&nbsp; Badminton
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(236,72,153,0.08);border:1px solid rgba(236,72,153,0.2);
                        border-radius:12px;padding:12px 14px;margin-bottom:16px;font-size:0.78em;color:#64748b;line-height:1.9;">
                <strong style="color:#f472b6;">Demo Coach Accounts:</strong><br>
                🎯 coach1 / coach123 &nbsp;·&nbsp; Team Alpha<br>
                🎯 coach2 / coach123 &nbsp;·&nbsp; Team Beta
            </div>""", unsafe_allow_html=True)

        # Login form
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Login →", use_container_width=True, type="primary"):
            role = st.session_state.login_role
            db   = USERS["players"] if role=="player" else USERS["coaches"]
            hashed = hashlib.md5(password.encode()).hexdigest()

            if username in db and db[username]["password"] == hashed:
                st.session_state.logged_in = True
                st.session_state.role      = role
                st.session_state.username  = username
                st.session_state.user_data = db[username]
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")

# ─── DASHBOARD HEADER ────────────────────────────────────────
def show_header():
    ud   = st.session_state.user_data
    role = st.session_state.role
    name = ud.get("name","User")
    badge_cls = "badge-player" if role=="player" else "badge-coach"
    badge_txt = "PLAYER" if role=="player" else "COACH"

    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"""
        <div class="dash-header">
            <div class="dash-header-left">
                <span style="font-size:1.5em;">⚡</span>
                <div class="dash-logo"><span>SPORTS AI</span> WEARABLE</div>
                <span style="display:flex;align-items:center;gap:6px;background:rgba(74,222,128,0.08);
                             border:1px solid rgba(74,222,128,0.2);color:#4ade80;
                             font-size:0.72em;font-weight:700;padding:4px 12px;border-radius:20px;">
                    <span class="live-dot"></span>LIVE
                </span>
            </div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;padding:14px 0;">
            <span style="font-size:0.82em;color:#64748b;">👋 {name}</span>
            <span class="user-role-badge {badge_cls}">{badge_txt}</span>
        </div>""", unsafe_allow_html=True)
        if st.button("Logout", type="secondary"):
            for k in ["logged_in","role","username","user_data"]:
                st.session_state[k] = False if k=="logged_in" else None
            st.session_state.user_data = {}
            st.rerun()

# ─── SHARED DASHBOARD CONTENT ────────────────────────────────
def show_dashboard(player_key, player_info, is_coach=False):
    max_hr       = player_info.get("max_hr", 190)
    sport        = player_info.get("sport", "Cricket")
    player_name  = player_info.get("name", "Player")

    # Read sensors
    wrist, wrist_real = read_sensor("../data/wrist_data.json", simulate_wrist)
    waist, waist_real = read_sensor("../data/waist_data.json", simulate_waist)
    ankle, ankle_real = read_sensor("../data/ankle_data.json", simulate_ankle)

    heart_rate  = wrist.get("heart_rate",70)
    spo2        = wrist.get("spo2",98)
    temperature = wrist.get("temperature",36.5)
    activity    = wrist.get("activity","Resting")
    ax          = wrist.get("accel_x",0)
    ay          = wrist.get("accel_y",0)
    az          = wrist.get("accel_z",0)
    steps_now   = wrist.get("steps",0) + ankle.get("steps",0)
    stride      = ankle.get("stride_length",0.0)
    cadence     = ankle.get("cadence",0)
    spine_tilt  = waist.get("spine_tilt",0)
    waist_pos   = waist.get("posture","Good")

    # Init session state for totals
    key = f"totals_{player_key}"
    if key not in st.session_state:
        st.session_state[key] = {"steps":0,"calories":0,"heart_data":[],"accel_x":[],"accel_y":[],"accel_z":[],"timestamps":[],"counts":{"Running":0,"Walking":0,"Jumping":0,"Resting":0},"start":time.time()}

    totals = st.session_state[key]
    totals["steps"]    += steps_now
    totals["calories"] += int(heart_rate * 0.05)
    totals["counts"][activity] = totals["counts"].get(activity,0)+1
    t = time.strftime("%H:%M:%S")
    totals["heart_data"].append(heart_rate)
    totals["accel_x"].append(ax); totals["accel_y"].append(ay); totals["accel_z"].append(az)
    totals["timestamps"].append(t)
    if len(totals["heart_data"])>30:
        totals["heart_data"].pop(0); totals["accel_x"].pop(0)
        totals["accel_y"].pop(0); totals["accel_z"].pop(0); totals["timestamps"].pop(0)

    session_secs = int(time.time()-totals["start"])
    session_time = f"{session_secs//60}m {session_secs%60}s"

    advice_list, hr_zone_pct, alert_level = analyze_performance(
        heart_rate, totals["steps"], activity, max_hr, spo2, temperature)

    # ── Coach alert banner ──
    if is_coach:
        if alert_level == "red":
            st.markdown(f"""
            <div class="alert-banner danger">
                <div class="alert-title">🚨 URGENT ALERT — {player_name}</div>
                <div class="alert-body">Heart rate critically high at {heart_rate} bpm! Consider substituting the player immediately.</div>
            </div>""", unsafe_allow_html=True)
        elif alert_level == "orange":
            st.markdown(f"""
            <div class="alert-banner warning">
                <div class="alert-title">⚠️ WARNING — {player_name}</div>
                <div class="alert-body">Player operating at high intensity ({hr_zone_pct}% of max HR). Monitor closely.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-banner good">
                <div class="alert-title">✅ {player_name} — Good Condition</div>
                <div class="alert-body">All vitals normal. Heart rate {heart_rate} bpm · SpO2 {spo2}% · Temp {temperature}°C</div>
            </div>""", unsafe_allow_html=True)

    # ── Device badges ──
    wl = "real" if wrist_real else "sim"; bl = "real" if waist_real else "sim"; al = "real" if ankle_real else "sim"
    wt = "REAL" if wrist_real else "SIM"; bt = "REAL" if waist_real else "SIM"; at_ = "REAL" if ankle_real else "SIM"
    st.markdown(f"""
    <div class="device-grid">
        <div class="device-card wrist"><div style="font-size:1.8em;">⌚</div>
            <div><div class="device-name">ESP32 #1 — WRIST</div><div class="device-info">MPU6050 + MAX30102</div></div>
            <div class="device-badge {wl}">{wt}</div></div>
        <div class="device-card waist"><div style="font-size:1.8em;">🎽</div>
            <div><div class="device-name">ESP32 #2 — WAIST</div><div class="device-info">MPU6050 · Posture</div></div>
            <div class="device-badge {bl}">{bt}</div></div>
        <div class="device-card ankle"><div style="font-size:1.8em;">👟</div>
            <div><div class="device-name">ESP32 #3 — ANKLE</div><div class="device-info">MPU6050 · Steps + Stride</div></div>
            <div class="device-badge {al}">{at_}</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Posture ──
    posture = {}
    try:
        with open("../data/posture_data.json","r") as f: posture = json.load(f)
        p_text=posture.get("posture",""); p_spine=posture.get("spine_angle",0)
        p_lknee=posture.get("left_knee",0); p_rknee=posture.get("right_knee",0)
        p_time=posture.get("timestamp","--"); p_count=posture.get("players",0)
        pcls="good" if "GOOD" in p_text else ("fair" if "FAIR" in p_text else "bad")
        st.markdown(f"""
        <div class="posture-wrap {pcls}">
            <div><div class="posture-title {pcls}">🦴 {p_text}</div>
                 <div class="posture-time">Camera · {p_time} · {p_count} player(s) · Waist tilt: {spine_tilt}°</div></div>
            <div class="angle-group">
                <div class="angle-chip"><div class="angle-num">{p_spine}°</div><div class="angle-tag">Spine</div></div>
                <div class="angle-chip"><div class="angle-num">{p_lknee}°</div><div class="angle-tag">L Knee</div></div>
                <div class="angle-chip"><div class="angle-num">{p_rknee}°</div><div class="angle-tag">R Knee</div></div>
                <div class="angle-chip"><div class="angle-num">{spine_tilt}°</div><div class="angle-tag">Waist</div></div>
            </div>
        </div>""", unsafe_allow_html=True)
    except:
        pcls="good" if waist_pos=="Good" else ("fair" if waist_pos=="Fair" else "bad")
        st.markdown(f"""
        <div class="posture-wrap {pcls}">
            <div><div class="posture-title {pcls}">🎽 Waist Sensor: {waist_pos}</div>
                 <div class="posture-time">Spine tilt: {spine_tilt}° · Run posture_detection.py for camera angles</div></div>
            <div class="angle-group">
                <div class="angle-chip"><div class="angle-num">{spine_tilt}°</div><div class="angle-tag">Waist</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── 6 Metrics ──
    st.markdown('<p class="sec-label">📊 Live Metrics</p>', unsafe_allow_html=True)
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.markdown(f'<div class="metric-card hr"><span class="metric-icon hb">❤️</span><div class="metric-val">{heart_rate}</div><div class="metric-lbl">Heart Rate</div><div class="metric-sub">bpm</div><div class="metric-bg">❤️</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card spo"><span class="metric-icon fl">🫀</span><div class="metric-val">{spo2}%</div><div class="metric-lbl">SpO2</div><div class="metric-sub">blood oxygen</div><div class="metric-bg">🫀</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card steps"><span class="metric-icon fl">👟</span><div class="metric-val">{totals["steps"]:,}</div><div class="metric-lbl">Steps</div><div class="metric-sub">total</div><div class="metric-bg">👟</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card act"><span class="metric-icon">🏃</span><div class="metric-val" style="font-size:1.3em;">{activity}</div><div class="metric-lbl">Activity</div><div class="metric-sub">now</div><div class="metric-bg">🏃</div></div>', unsafe_allow_html=True)
    m5.markdown(f'<div class="metric-card cal"><span class="metric-icon fl">🔥</span><div class="metric-val">{totals["calories"]:,}</div><div class="metric-lbl">Calories</div><div class="metric-sub">kcal</div><div class="metric-bg">🔥</div></div>', unsafe_allow_html=True)
    m6.markdown(f'<div class="metric-card tmp"><span class="metric-icon fl">🌡️</span><div class="metric-val">{temperature}°</div><div class="metric-lbl">Temp</div><div class="metric-sub">body °C</div><div class="metric-bg">🌡️</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── HR Chart + Pie ──
    r1l, r1r = st.columns([3,2])
    with r1l:
        st.markdown('<p class="sec-label">📈 Live Heart Rate</p>', unsafe_allow_html=True)
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(y=totals["heart_data"],x=totals["timestamps"],mode="lines+markers",
            line=dict(color="#818cf8",width=2.5,shape="spline",smoothing=1.3),
            marker=dict(size=5,color="#a5b4fc"),fill="tozeroy",fillcolor="rgba(99,102,241,0.08)"))
        fig_hr.add_hline(y=max_hr*0.9,line_dash="dot",line_color="#ef4444",line_width=1.5,annotation_text="Danger",annotation_font_color="#ef4444",annotation_font_size=11)
        fig_hr.add_hline(y=max_hr*0.75,line_dash="dot",line_color="#f97316",line_width=1.5,annotation_text="High",annotation_font_color="#f97316",annotation_font_size=11)
        fig_hr.update_layout(paper_bgcolor="#111827",plot_bgcolor="#111827",font=dict(color="#475569",family="Inter"),
            xaxis=dict(showgrid=False,tickfont=dict(size=10,color="#334155"),title=""),
            yaxis=dict(showgrid=True,gridcolor="#0f172a",title="BPM",range=[40,220],tickfont=dict(size=10,color="#334155")),
            margin=dict(l=10,r=10,t=10,b=30),height=260,showlegend=False)
        st.plotly_chart(fig_hr, use_container_width=True)

    with r1r:
        st.markdown('<p class="sec-label">🏃 Activity Split</p>', unsafe_allow_html=True)
        fig_pie = px.pie(values=list(totals["counts"].values()),names=list(totals["counts"].keys()),
            color_discrete_sequence=["#818cf8","#f472b6","#34d399","#fbbf24"],hole=0.52)
        fig_pie.update_traces(textfont_color="#e2e8f0",textfont_size=11,marker=dict(line=dict(color="#111827",width=2)))
        fig_pie.update_layout(paper_bgcolor="#111827",font=dict(color="#475569",family="Inter"),
            margin=dict(l=10,r=10,t=10,b=10),height=260,legend=dict(font=dict(color="#64748b",size=11),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── AI Coach + Stats ──
    r2l, r2r = st.columns([1,1])
    with r2l:
        st.markdown('<p class="sec-label">🤖 AI Coach Advice</p>', unsafe_allow_html=True)
        tips = "".join([f'<div class="coach-tip {alert_level}">› {t}</div>' for t in advice_list])
        st.markdown(f'<div class="coach-wrap">{tips}</div>', unsafe_allow_html=True)
    with r2r:
        st.markdown('<p class="sec-label">📊 Session Stats</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stats-wrap">
            <div class="stat-row"><span class="stat-key">🏅 Sport</span><span class="stat-val">{sport}</span></div>
            <div class="stat-row"><span class="stat-key">👤 Player</span><span class="stat-val">{player_name}</span></div>
            <div class="stat-row"><span class="stat-key">❤️ Heart Rate</span><span class="stat-val">{heart_rate} bpm</span></div>
            <div class="stat-row"><span class="stat-key">🫀 SpO2</span><span class="stat-val">{spo2}%</span></div>
            <div class="stat-row"><span class="stat-key">🌡️ Temp</span><span class="stat-val">{temperature}°C</span></div>
            <div class="stat-row"><span class="stat-key">📊 HR Zone</span><span class="stat-val">{hr_zone_pct}% of max</span></div>
            <div class="stat-row"><span class="stat-key">👟 Steps</span><span class="stat-val">{totals["steps"]:,}</span></div>
            <div class="stat-row"><span class="stat-key">🦵 Stride</span><span class="stat-val">{stride}m</span></div>
            <div class="stat-row" style="border:none"><span class="stat-key">⏱️ Duration</span><span class="stat-val">{session_time}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Accel + Waist + Ankle ──
    r3a, r3b, r3c = st.columns([3,2,2])
    with r3a:
        st.markdown('<p class="sec-label">📡 Wrist Acceleration</p>', unsafe_allow_html=True)
        fig_acc=go.Figure()
        fig_acc.add_trace(go.Scatter(y=totals["accel_x"],name="X",line=dict(color="#f87171",width=2,shape="spline")))
        fig_acc.add_trace(go.Scatter(y=totals["accel_y"],name="Y",line=dict(color="#34d399",width=2,shape="spline")))
        fig_acc.add_trace(go.Scatter(y=totals["accel_z"],name="Z",line=dict(color="#818cf8",width=2,shape="spline")))
        fig_acc.update_layout(paper_bgcolor="#111827",plot_bgcolor="#111827",font=dict(color="#475569",family="Inter"),
            xaxis=dict(showgrid=False,tickfont=dict(size=10,color="#334155")),
            yaxis=dict(showgrid=True,gridcolor="#0f172a",range=[-3,3],title="G-Force",tickfont=dict(size=10,color="#334155")),
            margin=dict(l=10,r=10,t=10,b=10),height=220,
            legend=dict(orientation="h",font=dict(color="#64748b",size=11),bgcolor="rgba(0,0,0,0)",y=-0.25))
        st.plotly_chart(fig_acc, use_container_width=True)
    with r3b:
        st.markdown('<p class="sec-label">🎽 Waist Sensor</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="waist-card">
            <div class="sensor-title">ESP32 #2 — Waist</div>
            <div class="sensor-row"><span class="sensor-key">🦴 Posture</span><span class="sensor-val">{waist_pos}</span></div>
            <div class="sensor-row"><span class="sensor-key">📐 Spine Tilt</span><span class="sensor-val">{spine_tilt}°</span></div>
            <div class="sensor-row"><span class="sensor-key">📡 Accel X</span><span class="sensor-val">{waist.get("accel_x",0)}g</span></div>
            <div class="sensor-row"><span class="sensor-key">📡 Accel Y</span><span class="sensor-val">{waist.get("accel_y",0)}g</span></div>
            <div class="sensor-row" style="border:none"><span class="sensor-key">📡 Accel Z</span><span class="sensor-val">{waist.get("accel_z",0)}g</span></div>
        </div>""", unsafe_allow_html=True)
    with r3c:
        st.markdown('<p class="sec-label">👟 Ankle Sensor</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ankle-card">
            <div class="sensor-title">ESP32 #3 — Ankle</div>
            <div class="sensor-row"><span class="sensor-key">👣 Steps</span><span class="sensor-val">{ankle.get("steps",0)}</span></div>
            <div class="sensor-row"><span class="sensor-key">🦵 Stride</span><span class="sensor-val">{stride}m</span></div>
            <div class="sensor-row"><span class="sensor-key">⚡ Cadence</span><span class="sensor-val">{cadence}/sec</span></div>
            <div class="sensor-row"><span class="sensor-key">📡 Accel X</span><span class="sensor-val">{ankle.get("accel_x",0)}g</span></div>
            <div class="sensor-row" style="border:none"><span class="sensor-key">🏃 Activity</span><span class="sensor-val">{ankle.get("foot_activity","—")}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Zone Bar ──
    st.markdown('<p class="sec-label">💓 Heart Rate Zone</p>', unsafe_allow_html=True)
    zc={"red":"#ef4444","orange":"#f97316","green":"#22c55e","blue":"#6366f1"}
    bc=zc.get(alert_level,"#818cf8")
    if   hr_zone_pct<50: p1,p2,p3,p4="zp-rest","zp-off","zp-off","zp-off"
    elif hr_zone_pct<75: p1,p2,p3,p4="zp-off","zp-mod","zp-off","zp-off"
    elif hr_zone_pct<90: p1,p2,p3,p4="zp-off","zp-off","zp-high","zp-off"
    else:                p1,p2,p3,p4="zp-off","zp-off","zp-off","zp-danger"
    st.markdown(f"""
    <div class="zone-wrap">
        <div class="zone-header">
            <span style="font-size:0.8em;color:#475569;text-transform:uppercase;letter-spacing:1.5px;">Current Zone</span>
            <span style="font-size:0.85em;font-weight:600;color:{bc};">{hr_zone_pct}% of max HR ({max_hr} bpm)</span>
        </div>
        <div class="zone-scale"><span>Rest</span><span>50%</span><span>75%</span><span>90%</span><span>Max</span></div>
        <div class="zone-track"><div class="zone-fill" style="width:{min(hr_zone_pct,100)}%;background:linear-gradient(90deg,#6366f1,{bc});"></div></div>
        <div class="zone-pills">
            <div class="zone-pill {p1}">🔵 Rest &lt;50%</div>
            <div class="zone-pill {p2}">🟢 Moderate 50–75%</div>
            <div class="zone-pill {p3}">🟠 High 75–90%</div>
            <div class="zone-pill {p4}">🔴 Danger &gt;90%</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Session History ──
    st.markdown('<p class="sec-label">📋 Previous Sessions</p>', unsafe_allow_html=True)
    try:
        with open("../data/session_history.json","r") as f: history=json.load(f)
        if not history:
            st.markdown('<div class="history-wrap"><p class="no-data">No previous sessions yet!</p></div>', unsafe_allow_html=True)
        else:
            rows=""
            for s in reversed(history[-5:]):
                avg=s.get("avg_hr",0); peak=s.get("peak_hr",0)
                st_=s.get("total_steps",0); cal_=s.get("total_calories",0)
                dur=s.get("duration_secs",0); ds=f"{dur//60}m {dur%60}s"
                acts=", ".join(s.get("activities",[]))
                rows+=f"""
                <div class="history-item">
                    <div>
                        <div class="hist-date">📅 {s['date']} · 🕐 {s['time']}</div>
                        <div class="hist-meta">⏱️ {ds} · 🏃 {acts}</div>
                    </div>
                    <div class="hist-stats">
                        <div class="hst"><div class="hst-val" style="color:#fca5a5;">{avg}</div><div class="hst-lbl">Avg HR</div></div>
                        <div class="hst"><div class="hst-val" style="color:#c4b5fd;">{peak}</div><div class="hst-lbl">Peak</div></div>
                        <div class="hst"><div class="hst-val" style="color:#93c5fd;">{st_:,}</div><div class="hst-lbl">Steps</div></div>
                        <div class="hst"><div class="hst-val" style="color:#fdba74;">{cal_:,}</div><div class="hst-lbl">kcal</div></div>
                    </div>
                </div>"""
            st.markdown(f'<div class="history-wrap">{rows}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="history-wrap"><p class="no-data">No sessions yet!</p></div>', unsafe_allow_html=True)

# ─── COACH VIEW ───────────────────────────────────────────────
def show_coach_view():
    ud   = st.session_state.user_data
    show_header()

    st.markdown('<div class="dash-body">', unsafe_allow_html=True)

    # Tab: All Players Overview / Individual Player
    tab1, tab2 = st.tabs(["👥 All Players Overview", "🔍 Individual Player"])

    with tab1:
        st.markdown('<p class="sec-label">👥 All Players — Live Status</p>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(pk,pinfo) in enumerate(USERS["players"].items()):
            wrist,_ = read_sensor("../data/wrist_data.json", simulate_wrist)
            hr  = wrist.get("heart_rate",70)
            sp  = wrist.get("spo2",98)
            tmp = wrist.get("temperature",36.5)
            act = wrist.get("activity","Resting")
            _,hrz,alv = analyze_performance(hr,0,act,pinfo["max_hr"])
            status_color = {"red":"#ef4444","orange":"#f97316","green":"#22c55e","blue":"#6366f1"}.get(alv,"#818cf8")
            with cols[i%3]:
                st.markdown(f"""
                <div class="player-overview-card" style="margin-bottom:12px;">
                    <div class="poc-header">
                        <div>
                            <div class="poc-name">{pinfo['name']} {pinfo['jersey']}</div>
                            <div class="poc-sport">🏅 {pinfo['sport']}</div>
                        </div>
                        <span style="color:{status_color};font-size:1.4em;">●</span>
                    </div>
                    <div class="poc-stats">
                        <div class="poc-stat">
                            <div class="poc-val" style="color:#fca5a5;">{hr}</div>
                            <div class="poc-lbl">HR bpm</div>
                        </div>
                        <div class="poc-stat">
                            <div class="poc-val" style="color:#86efac;">{sp}%</div>
                            <div class="poc-lbl">SpO2</div>
                        </div>
                        <div class="poc-stat">
                            <div class="poc-val" style="color:#f9a8d4;">{tmp}°</div>
                            <div class="poc-lbl">Temp</div>
                        </div>
                    </div>
                    <div style="margin-top:10px;font-size:0.75em;color:{status_color};font-weight:600;">
                        {act} · {hrz}% of max HR
                    </div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown('<p class="sec-label">🔍 Select Player to Monitor</p>', unsafe_allow_html=True)
        player_keys = list(USERS["players"].keys())
        sel = st.selectbox("Choose Player", player_keys,
                           format_func=lambda x: f"{USERS['players'][x]['name']} — {USERS['players'][x]['sport']}")
        st.session_state.sel_player = sel
        show_dashboard(sel, USERS["players"][sel], is_coach=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─── PLAYER VIEW ──────────────────────────────────────────────
def show_player_view():
    show_header()
    st.markdown('<div class="dash-body">', unsafe_allow_html=True)
    username = st.session_state.username
    user_data = st.session_state.user_data
    show_dashboard(username, user_data, is_coach=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── MAIN ─────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
else:
    if st.session_state.role == "coach":
        show_coach_view()
        time.sleep(2)
        st.rerun()
    else:
        show_player_view()
        time.sleep(2)
        st.rerun()
