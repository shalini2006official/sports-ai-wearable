import React, { useState, useEffect, useMemo, useRef } from "react";
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar,
} from "recharts";
import {
  Activity, Heart, Wind, Zap, TrendingUp, Users, Radio, Bell, Settings,
  LogOut, Search, ChevronDown, ChevronRight, ChevronLeft, Menu, X, Award,
  ShieldAlert, Info, AlertTriangle, Droplet, Moon, Sun, Wifi, WifiOff,
  Play, ArrowRight, CheckCircle2, Lock, Star, Clock, Gauge, Flame,
  BarChart3, User, Eye, EyeOff, Trophy,Video
} from "lucide-react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import VideoAnalysis from "./pages/VideoAnalysis";

/* ============================== DESIGN TOKENS ============================== */
const C = {
  void: "#060A12",
  panel: "#0B1220",
  panel2: "#0F1830",
  border: "rgba(148,178,222,0.12)",
  borderBright: "rgba(94,234,255,0.35)",
  cyan: "#22D3EE",
  blue: "#3B82F6",
  pulse: "#FB7185",
  green: "#34D399",
  amber: "#FBBF24",
  text: "#E7EEF9",
  muted: "#7E8CA6",
  muted2: "#54607A",
};

const FontStyles = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    .f-display { font-family: 'Space Grotesk', sans-serif; }
    .f-body { font-family: 'Inter', sans-serif; }
    .f-mono { font-family: 'JetBrains Mono', monospace; }
    * { scrollbar-width: thin; scrollbar-color: rgba(94,234,255,0.25) transparent; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-thumb { background: rgba(94,234,255,0.25); border-radius: 4px; }
    @keyframes dash { to { stroke-dashoffset: -400; } }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(14px);} to {opacity:1; transform:translateY(0);} }
    @keyframes pulseDot { 0%,100% { opacity:1; } 50% { opacity:0.35; } }
    @keyframes floaty { 0%,100% { transform: translateY(0);} 50% { transform: translateY(-6px);} }
    .fade-up { animation: fadeUp 0.6s ease both; }
    .pulse-dot { animation: pulseDot 1.6s ease-in-out infinite; }
    .floaty { animation: floaty 4s ease-in-out infinite; }
    @media (prefers-reduced-motion: reduce) {
      .fade-up, .pulse-dot, .floaty { animation: none !important; }
    }
  `}</style>
);

/* ============================== SIGNATURE: ECG LINE ============================== */
function ECGLine({ color = C.pulse, height = 60, opacity = 1, strokeWidth = 2 }) {
  const path = "M0,30 L40,30 L52,30 L58,8 L66,52 L74,14 L80,30 L100,30 L140,30 L152,30 L158,8 L166,52 L174,14 L180,30 L200,30 L240,30 L252,30 L258,8 L266,52 L274,14 L280,30 L300,30 L340,30 L352,30 L358,8 L366,52 L374,14 L380,30 L400,30";
  return (
    <svg viewBox="0 0 400 60" width="100%" height={height} preserveAspectRatio="none" style={{ opacity }}>
      <path d={path} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round"
        strokeDasharray="14 8" style={{ animation: "dash 3.2s linear infinite" }} />
    </svg>
  );
}

/* ============================== HELPERS ============================== */
function hashNoise(seed, t) {
  const x = Math.sin(seed * 12.9898 + t * 78.233) * 43758.5453;
  return (x - Math.floor(x)) * 2 - 1;
}
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function telemetryAt(seed, t, fitnessBase) {
  const ph = seed * 13.7;
  const n1 = hashNoise(seed, t);
  const n2 = hashNoise(seed + 50, t * 1.3);
  const hr = clamp(72 + (seed % 5) * 2 + 20 * Math.sin((t + ph) / 9) + 9 * Math.sin((t + ph) / 3.1) + n1 * 4, 54, 192);
  const spo2 = clamp(98 - Math.abs(Math.sin((t + ph) / 15)) * 2.4 + n2 * 0.5, 90, 100);
  const accelX = Math.sin((t + ph) / 2) * (0.6 + (hr - 70) / 55) + n1 * 0.25;
  const accelY = Math.cos((t + ph) / 2.3) * (0.6 + (hr - 70) / 60) + n2 * 0.25;
  const accelZ = 9.8 + n1 * 0.15;
  const gyroX = Math.sin((t + ph) / 1.6) * (10 + (hr - 70) / 3) + n2 * 3;
  const gyroY = Math.cos((t + ph) / 1.9) * (8 + (hr - 70) / 4) + n1 * 3;
  const gyroZ = Math.sin((t + ph) / 2.4) * 6 + n2 * 2;
  const movement = Math.sqrt(accelX * accelX + accelY * accelY) * 10;
  let activity = "Idle";
  if (movement > 9) activity = "Sprinting";
  else if (movement > 5.5) activity = "Running";
  else if (movement > 2.2) activity = "Walking";
  const fatigue = clamp(28 + (hr - 75) * 0.55 + 14 * Math.sin((t + ph) / 30) + n2 * 3, 4, 98);
  const performance = clamp(fitnessBase + (hr > 95 && hr < 165 ? 6 : -4) - fatigue * 0.25 + n1 * 3, 35, 99);
  return {
    hr: Math.round(hr), spo2: Math.round(spo2 * 10) / 10,
    accel: { x: Math.round(accelX * 100) / 100, y: Math.round(accelY * 100) / 100, z: Math.round(accelZ * 100) / 100 },
    gyro: { x: Math.round(gyroX * 10) / 10, y: Math.round(gyroY * 10) / 10, z: Math.round(gyroZ * 10) / 10 },
    movement: Math.round(movement * 10) / 10, activity,
    fatigue: Math.round(fatigue), performance: Math.round(performance),
    fitness: Math.round(clamp(fitnessBase + n1 * 2, 40, 99)),
  };
}

/* ============================== LIVE BACKEND CONNECTION ==============================
   Points at the Flask API in server.py. Only reachable when this file is run as a real
   app (e.g. `npm run dev`) on the same machine as the backend — the Claude.ai artifact
   preview cannot reach localhost, so it will always fall back to simulated data here. */
const API_BASE = "http://localhost:5000";
const LIVE_POLL_MS = 2000;

function useLiveTelemetry(seed, fitnessBase, tick) {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [source, setSource] = useState("simulated"); // "live" | "simulated" | "connecting"

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${API_BASE}/api/sensors/live`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!res.ok) throw new Error("bad response");
        const json = await res.json();
        if (cancelled) return;
        const fitness = Math.round(clamp(100 - json.fatigue * 0.35, 40, 99));
        const shaped = { ...json, fitness };
        setData(shaped);
        setSource("live");
        setHistory((h) => [...h.slice(-23), { t: json.timestamp, hr: json.hr, spo2: json.spo2, movement: json.movement }]);
      } catch (e) {
    console.error("Backend Error:", e);
        if (cancelled) return;
        // Backend unreachable (expected inside the artifact preview) — use built-in simulation
        const t = telemetryAt(seed, tick, fitnessBase);
        setData(t);
        setSource("simulated");
        setHistory((h) => [...h.slice(-23), { t: `${tick}`, hr: t.hr, spo2: t.spo2, movement: t.movement }]);
      }
    }

    poll();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick]);

  return { data, history, source };
}

const PLAYERS = [
  { id: 1, name: "Alex Carter", jersey: 7, position: "Forward", seed: 1, fitnessBase: 88 },
  { id: 2, name: "Maya Chen", jersey: 11, position: "Midfielder", seed: 2, fitnessBase: 91 },
  { id: 3, name: "Jordan Blake", jersey: 4, position: "Defender", seed: 3, fitnessBase: 79 },
  { id: 4, name: "Sam Okafor", jersey: 9, position: "Forward", seed: 4, fitnessBase: 85 },
  { id: 5, name: "Riley Novak", jersey: 2, position: "Defender", seed: 5, fitnessBase: 74 },
  { id: 6, name: "Priya Menon", jersey: 14, position: "Midfielder", seed: 6, fitnessBase: 93 },
  { id: 7, name: "Theo Reyes", jersey: 21, position: "Goalkeeper", seed: 7, fitnessBase: 82 },
  { id: 8, name: "Nina Kowalski", jersey: 17, position: "Midfielder", seed: 8, fitnessBase: 87 },
];

function aiMessagesFor(t) {
  const msgs = [];
  if (t.hr > 165) msgs.push({ p: "critical", icon: Heart, text: `Heart rate at ${t.hr} BPM is well above normal training zone. Consider easing intensity now.` });
  if (t.spo2 < 94) msgs.push({ p: "critical", icon: Wind, text: `SpO₂ dropped to ${t.spo2}%. Slow your breathing and check in with staff if this persists.` });
  if (t.fatigue > 72) msgs.push({ p: "warning", icon: Flame, text: `Fatigue is trending high at ${t.fatigue}%. A short recovery break will protect today's performance.` });
  if (t.movement > 8 && t.gyro.x > 20) msgs.push({ p: "warning", icon: ShieldAlert, text: "Unusual rotational movement detected — a common precursor to ankle or knee strain. Watch your footing." });
  if (msgs.length < 2) msgs.push({ p: "info", icon: Droplet, text: "You're 40 minutes into activity — a hydration break now will keep performance steady." });
  if (msgs.length < 3) msgs.push({ p: "info", icon: TrendingUp, text: `Heart rate is sitting in a strong training zone. Great window to push a controlled interval.` });
  msgs.push({ p: "info", icon: Moon, text: "Cool down with 5 minutes of light movement and stretching before you finish today." });
  return msgs.slice(0, 4);
}

const SESSIONS = [
  { date: "Jul 10, 2026", duration: "58 min", avgHr: 138, avgSpo2: 97, score: 88, activity: "Match" },
  { date: "Jul 8, 2026", duration: "42 min", avgHr: 121, avgSpo2: 98, score: 81, activity: "Training" },
  { date: "Jul 6, 2026", duration: "35 min", avgHr: 109, avgSpo2: 98, score: 76, activity: "Recovery" },
  { date: "Jul 3, 2026", duration: "61 min", avgHr: 145, avgSpo2: 96, score: 91, activity: "Match" },
  { date: "Jul 1, 2026", duration: "50 min", avgHr: 132, avgSpo2: 97, score: 84, activity: "Training" },
];

const BADGES = [
  { name: "Iron Lungs", desc: "SpO₂ above 97% for a full session", icon: Wind, earned: true },
  { name: "Steady Heart", desc: "Resting HR under 65 BPM", icon: Heart, earned: true },
  { name: "Century Club", desc: "100 sessions logged", icon: Award, earned: false },
  { name: "Sprint King", desc: "Peak movement intensity in top 5%", icon: Zap, earned: true },
  { name: "Comeback", desc: "Fatigue recovery under 10 minutes", icon: TrendingUp, earned: false },
  { name: "Perfect Week", desc: "7 straight days of logged activity", icon: Star, earned: true },
];

/* ============================== SMALL UI PRIMITIVES ============================== */
function GlassCard({ children, className = "", style = {}, glow }) {
  return (
    <div className={`rounded-2xl backdrop-blur-md ${className}`}
      style={{
        background: "linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015))",
        border: `1px solid ${glow ? C.borderBright : C.border}`,
        boxShadow: glow ? `0 0 0 1px rgba(94,234,255,0.06), 0 12px 40px -12px rgba(34,211,238,0.25)` : "0 8px 30px -18px rgba(0,0,0,0.6)",
        ...style,
      }}>
      {children}
    </div>
  );
}

function Ring({ value, size = 76, stroke = 7, color = C.cyan, label, sub }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const off = c - (clamp(value, 0, 100) / 100) * c;
  return (
    <div className="flex flex-col items-center justify-center">
      <div style={{ position: "relative", width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
          <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={stroke} />
          <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
            strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 0.8s ease" }} />
        </svg>
        <div style={{ position: "absolute", inset: 0 }} className="flex items-center justify-center f-mono font-semibold" >
          <span style={{ color: C.text, fontSize: size * 0.22 }}>
  {sub ? parseInt(sub) : Math.round(value)}
</span>
        </div>
      </div>
      {label && <div className="f-body text-xs mt-2 text-center" style={{ color: C.muted }}>{label}</div>}
      {sub && <div className="f-mono text-[11px]" style={{ color: C.muted2 }}>{sub}</div>}
    </div>
  );
}

function PriorityBadge({ p }) {
  const map = {
    critical: { bg: "rgba(251,113,133,0.12)", fg: C.pulse, label: "Critical", Icon: AlertTriangle },
    warning: { bg: "rgba(251,191,36,0.12)", fg: C.amber, label: "Warning", Icon: ShieldAlert },
    info: { bg: "rgba(34,211,238,0.12)", fg: C.cyan, label: "Info", Icon: Info },
  };
  const m = map[p];
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] f-body font-medium"
      style={{ background: m.bg, color: m.fg }}>
      <m.Icon size={11} /> {m.label}
    </span>
  );
}

function StatChip({ icon: Icon, label, value, unit, color }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-xl" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${C.border}` }}>
      <div className="p-2 rounded-lg" style={{ background: `${color}1A` }}><Icon size={16} color={color} /></div>
      <div>
        <div className="f-mono text-lg font-semibold" style={{ color: C.text, lineHeight: 1 }}>{value}<span className="text-xs ml-1" style={{ color: C.muted }}>{unit}</span></div>
        <div className="f-body text-[11px]" style={{ color: C.muted }}>{label}</div>
      </div>
    </div>
  );
}

function ConnDot({ connected }) {
  return (
    <span className="inline-flex items-center gap-1.5 f-body text-xs" style={{ color: connected ? C.green : C.pulse }}>
      <span className="w-2 h-2 rounded-full pulse-dot" style={{ background: connected ? C.green : C.pulse }} />
      {connected ? "Connected" : "Offline"}
    </span>
  );
}

/* ============================== LANDING PAGE ============================== */
function Landing({ onGetStarted }) {
  const [openFaq, setOpenFaq] = useState(0);
  const faqs = [
    { q: "What hardware does this run on?", a: "An ESP32 microcontroller paired with an MPU6050 motion sensor and a MAX30102 heart-rate and SpO₂ sensor, streaming live telemetry over WiFi." },
    { q: "How fast is the data?", a: "Readings stream continuously with no page refresh needed — dashboards update as soon as new samples arrive." },
    { q: "Can a coach see the whole team at once?", a: "Yes. The coach dashboard aggregates every connected player's vitals, activity, and fatigue into one live view." },
    { q: "Does the AI coach replace a real coach?", a: "No — it flags patterns in real time (fatigue, irregular heart rate, risky movement) so human coaches can act faster." },
  ];
  const features = [
    { icon: Heart, title: "Live Vitals", desc: "Heart rate and SpO₂ streamed straight from the wearable, sample by sample." },
    { icon: Activity, title: "Motion Intelligence", desc: "Accelerometer and gyroscope data classify activity from idle to full sprint." },
    { icon: Zap, title: "AI Coaching", desc: "Personalized, priority-ranked guidance generated from your own sensor patterns." },
    { icon: ShieldAlert, title: "Injury Prevention", desc: "Unusual movement signatures are flagged before they become a strain." },
  ];
  return (
    <div className="min-h-screen f-body" style={{ background: C.void, color: C.text }}>
      <FontStyles />
      {/* Nav */}
      <nav className="sticky top-0 z-30 flex items-center justify-between px-6 md:px-12 py-4" style={{ background: "rgba(6,10,18,0.75)", backdropFilter: "blur(10px)", borderBottom: `1px solid ${C.border}` }}>
        <div className="flex items-center gap-2 f-display font-semibold text-lg">
          <Activity color={C.cyan} size={22} /> Sports<span style={{ color: C.cyan }}>AI</span> Wearable
        </div>
        <div className="hidden md:flex items-center gap-8 f-body text-sm" style={{ color: C.muted }}>
          <a href="#features" className="hover:text-white transition">Features</a>
          <a href="#how" className="hover:text-white transition">How It Works</a>
          <a href="#testimonials" className="hover:text-white transition">Testimonials</a>
          <a href="#faq" className="hover:text-white transition">FAQ</a>
        </div>
        <button onClick={onGetStarted} className="px-4 py-2 rounded-full f-body text-sm font-medium transition hover:opacity-90"
          style={{ background: `linear-gradient(135deg, ${C.cyan}, ${C.blue})`, color: "#04121A" }}>
          Get Started
        </button>
      </nav>

      {/* Hero */}
      <header className="relative px-6 md:px-12 pt-16 pb-24 overflow-hidden">
        <div className="absolute inset-x-0 top-24 opacity-30 pointer-events-none">
          <ECGLine color={C.pulse} height={120} strokeWidth={1.5} />
        </div>
        <div className="relative max-w-3xl mx-auto text-center fade-up">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs f-mono mb-6" style={{ border: `1px solid ${C.border}`, color: C.cyan }}>
            <Radio size={12} className="pulse-dot" /> LIVE TELEMETRY · ESP32 + MPU6050 + MAX30102
          </div>
          <h1 className="f-display font-semibold leading-tight text-4xl md:text-6xl">
            Every heartbeat, every stride,<br />
            <span style={{ color: C.cyan }}>read in real time.</span>
          </h1>
          <p className="mt-6 f-body text-base md:text-lg" style={{ color: C.muted }}>
            A wearable analytics platform that turns raw motion and vitals data into live coaching insight —
            for the athlete on the field and the coach on the sideline.
          </p>
          <div className="mt-9 flex items-center justify-center gap-4">
            <button onClick={onGetStarted} className="flex items-center gap-2 px-6 py-3 rounded-full f-body font-medium transition hover:opacity-90"
              style={{ background: `linear-gradient(135deg, ${C.cyan}, ${C.blue})`, color: "#04121A" }}>
              Get Started <ArrowRight size={16} />
            </button>
            <a href="#how" className="flex items-center gap-2 px-6 py-3 rounded-full f-body font-medium" style={{ border: `1px solid ${C.border}`, color: C.text }}>
              <Play size={15} /> See How It Works
            </a>
          </div>
        </div>

        {/* Live demo stat strip */}
        <div className="relative max-w-4xl mx-auto mt-16 grid grid-cols-2 md:grid-cols-4 gap-3 fade-up">
          <StatChip icon={Heart} label="Heart Rate" value="142" unit="BPM" color={C.pulse} />
          <StatChip icon={Wind} label="SpO₂" value="98" unit="%" color={C.cyan} />
          <StatChip icon={Activity} label="Movement" value="Running" unit="" color={C.blue} />
          <StatChip icon={Gauge} label="Activity Level" value="High" unit="" color={C.green} />
        </div>
      </header>

      {/* Features */}
      <section id="features" className="px-6 md:px-12 py-20" style={{ borderTop: `1px solid ${C.border}` }}>
        <div className="max-w-6xl mx-auto">
          <div className="mb-12 max-w-lg">
            <h2 className="f-display text-2xl md:text-3xl font-semibold">Built around the sensors, not the spreadsheet</h2>
            <p className="mt-3 f-body text-sm" style={{ color: C.muted }}>Four pillars, one continuous stream of live data.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((f, i) => (
              <GlassCard key={i} className="p-6">
                <div className="p-2.5 rounded-lg inline-flex mb-4" style={{ background: `${C.cyan}1A` }}>
                  <f.icon size={20} color={C.cyan} />
                </div>
                <h3 className="f-display font-semibold text-base">{f.title}</h3>
                <p className="mt-2 f-body text-sm" style={{ color: C.muted }}>{f.desc}</p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="px-6 md:px-12 py-20" style={{ borderTop: `1px solid ${C.border}` }}>
        <div className="max-w-6xl mx-auto">
          <h2 className="f-display text-2xl md:text-3xl font-semibold mb-12 text-center">How it works</h2>
          <div className="grid md:grid-cols-3 gap-8 relative">
            {[
              { t: "Wear it", d: "The ESP32 wearable rides comfortably during training, syncing motion and vitals sensors continuously." },
              { t: "Stream in real time", d: "Heart rate, SpO₂, acceleration, and gyroscope data flow in over WiFi with no manual refresh." },
              { t: "Get AI insight", d: "The AI coach reads the pattern and surfaces the one thing to do next — hydrate, ease off, or push on." },
            ].map((s, i) => (
              <div key={i} className="fade-up" style={{ animationDelay: `${i * 0.12}s` }}>
                <div className="f-mono text-xs mb-3" style={{ color: C.cyan }}>STEP {i + 1}</div>
                <h3 className="f-display font-semibold text-lg">{s.t}</h3>
                <p className="mt-2 f-body text-sm" style={{ color: C.muted }}>{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why choose us */}
      <section className="px-6 md:px-12 py-20" style={{ borderTop: `1px solid ${C.border}` }}>
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h2 className="f-display text-2xl md:text-3xl font-semibold">Why teams choose Sports AI Wearable</h2>
            <ul className="mt-6 space-y-4">
              {["Sub-second sensor updates, no polling delay", "Separate, purpose-built views for athletes and coaches", "Injury-risk pattern detection, not just raw numbers", "Works across desktop, tablet, and mobile sidelines"].map((t, i) => (
                <li key={i} className="flex items-start gap-3 f-body text-sm" style={{ color: C.muted }}>
                  <CheckCircle2 size={17} color={C.green} className="mt-0.5 flex-shrink-0" /> {t}
                </li>
              ))}
            </ul>
          </div>
          <GlassCard className="p-6 floaty">
            <ECGLine color={C.cyan} height={90} />
            <div className="grid grid-cols-3 gap-3 mt-2">
              <Ring value={78} size={70} color={C.pulse} label="HR Zone" />
              <Ring value={96} size={70} color={C.cyan} label="SpO₂" />
              <Ring value={64} size={70} color={C.blue} label="Fitness" />
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="px-6 md:px-12 py-20" style={{ borderTop: `1px solid ${C.border}` }}>
        <div className="max-w-6xl mx-auto">
          <h2 className="f-display text-2xl md:text-3xl font-semibold mb-12 text-center">Trusted on the sideline</h2>
          <div className="grid md:grid-cols-3 gap-5">
            {[
              { n: "Head Coach, Regional Academy", q: "We catch fatigue before it becomes an injury report now, not after." },
              { n: "Performance Analyst", q: "The live view during matches changed how we make substitutions." },
              { n: "Club Physiotherapist", q: "The movement alerts give us a head start we never had before." },
            ].map((t, i) => (
              <GlassCard key={i} className="p-6">
                <div className="flex gap-1 mb-3">{Array.from({ length: 5 }).map((_, j) => <Star key={j} size={13} fill={C.amber} color={C.amber} />)}</div>
                <p className="f-body text-sm italic" style={{ color: C.text }}>"{t.q}"</p>
                <p className="f-body text-xs mt-4" style={{ color: C.muted }}>{t.n}</p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="px-6 md:px-12 py-20" style={{ borderTop: `1px solid ${C.border}` }}>
        <div className="max-w-2xl mx-auto">
          <h2 className="f-display text-2xl md:text-3xl font-semibold mb-10 text-center">Frequently asked questions</h2>
          <div className="space-y-3">
            {faqs.map((f, i) => (
              <GlassCard key={i} className="overflow-hidden">
                <button className="w-full flex items-center justify-between px-5 py-4 text-left" onClick={() => setOpenFaq(openFaq === i ? -1 : i)}>
                  <span className="f-body text-sm font-medium">{f.q}</span>
                  <ChevronDown size={16} style={{ transform: openFaq === i ? "rotate(180deg)" : "none", transition: "0.2s", color: C.muted }} />
                </button>
                {openFaq === i && <p className="px-5 pb-4 f-body text-sm" style={{ color: C.muted }}>{f.a}</p>}
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Contact / CTA */}
      <section id="contact" className="px-6 md:px-12 py-20" style={{ borderTop: `1px solid ${C.border}` }}>
        <GlassCard className="max-w-4xl mx-auto p-10 text-center" glow>
          <h2 className="f-display text-2xl md:text-3xl font-semibold">Ready to see your team live?</h2>
          <p className="mt-3 f-body text-sm" style={{ color: C.muted }}>Sign in as a player or a coach to open the dashboard.</p>
          <button onClick={onGetStarted} className="mt-7 inline-flex items-center gap-2 px-6 py-3 rounded-full f-body font-medium transition hover:opacity-90"
            style={{ background: `linear-gradient(135deg, ${C.cyan}, ${C.blue})`, color: "#04121A" }}>
            Get Started <ArrowRight size={16} />
          </button>
        </GlassCard>
      </section>

      <footer className="px-6 md:px-12 py-10 flex flex-col md:flex-row items-center justify-between gap-4" style={{ borderTop: `1px solid ${C.border}`, color: C.muted2 }}>
        <div className="flex items-center gap-2 f-display text-sm"><Activity size={16} color={C.cyan} /> Sports AI Wearable</div>
        <p className="f-body text-xs">© 2026 Sports AI Wearable. Demo interface — sensor data simulated.</p>
      </footer>
    </div>
  );
}

/* ============================== LOGIN ============================== */
function LoginPage({ onLogin, onBack }) {
  const [role, setRole] = useState("player");
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [remember, setRemember] = useState(true);

  const submit = () => {
    onLogin(role, email || (role === "player" ? "alex.carter@club.io" : "coach@club.io"));
  };

  return (
    <div className="min-h-screen flex items-center justify-center f-body px-4 relative overflow-hidden" style={{ background: C.void, color: C.text }}>
      <FontStyles />
      <div className="absolute inset-x-0 top-10 opacity-20 pointer-events-none"><ECGLine color={C.cyan} height={140} /></div>
      <button onClick={onBack} className="absolute top-6 left-6 flex items-center gap-1 text-sm f-body" style={{ color: C.muted }}>
        <ChevronLeft size={16} /> Back
      </button>
      <GlassCard className="w-full max-w-md p-8 relative fade-up" glow>
        <div className="flex items-center gap-2 f-display font-semibold text-lg justify-center mb-1">
          <Activity color={C.cyan} size={20} /> Sports<span style={{ color: C.cyan }}>AI</span>
        </div>
        <p className="text-center f-body text-xs mb-6" style={{ color: C.muted }}>Sign in to your dashboard</p>

        <div className="grid grid-cols-2 gap-2 mb-6 p-1 rounded-xl" style={{ background: "rgba(255,255,255,0.04)" }}>
          {["player", "coach"].map((r) => (
            <button key={r} onClick={() => setRole(r)}
              className="py-2 rounded-lg f-body text-sm font-medium capitalize transition"
              style={{ background: role === r ? `linear-gradient(135deg, ${C.cyan}, ${C.blue})` : "transparent", color: role === r ? "#04121A" : C.muted }}>
              {r} Login
            </button>
          ))}
        </div>

        <div className="space-y-4">
          <div>
            <label className="f-body text-xs" style={{ color: C.muted }}>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder={role === "player" ? "alex.carter@club.io" : "coach@club.io"}
              className="mt-1 w-full px-3 py-2.5 rounded-lg f-body text-sm outline-none"
              style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}`, color: C.text }} />
          </div>
          <div>
            <label className="f-body text-xs" style={{ color: C.muted }}>Password</label>
            <div className="relative mt-1">
              <input value={pw} onChange={(e) => setPw(e.target.value)} type={showPw ? "text" : "password"} placeholder="••••••••"
                onKeyDown={(e) => { if (e.key === "Enter") submit(); }}
                className="w-full px-3 py-2.5 rounded-lg f-body text-sm outline-none pr-10"
                style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}`, color: C.text }} />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-2.5" style={{ color: C.muted }}>
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div className="flex items-center justify-between text-xs f-body" style={{ color: C.muted }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={remember} onChange={() => setRemember(!remember)} /> Remember me
            </label>
            <a href="#" className="hover:text-white transition" style={{ color: C.cyan }}>Forgot password?</a>
          </div>
          <button type="button" onClick={submit} className="w-full py-2.5 rounded-lg f-body font-medium text-sm transition hover:opacity-90"
            style={{ background: `linear-gradient(135deg, ${C.cyan}, ${C.blue})`, color: "#04121A" }}>
            Sign in as {role === "player" ? "Player" : "Coach"}
          </button>
        </div>
      </GlassCard>
    </div>
  );
}

/* ============================== SHELL (sidebar + topbar) ============================== */
function Sidebar({ items, active, setActive, collapsed, setCollapsed, onLogout, roleLabel, name }) {
  return (
    <div className="flex flex-col h-full" style={{ width: collapsed ? 72 : 232, transition: "width 0.2s", background: C.panel, borderRight: `1px solid ${C.border}` }}>
      <div className="flex items-center gap-2 px-4 py-5" style={{ borderBottom: `1px solid ${C.border}` }}>
        <Activity color={C.cyan} size={22} className="flex-shrink-0" />
        {!collapsed && <span className="f-display font-semibold text-sm truncate">Sports<span style={{ color: C.cyan }}>AI</span></span>}
      </div>
      <nav className="flex-1 py-4 px-2 space-y-1">
        {items.map((it) => (
          <button key={it.key} onClick={() => setActive(it.key)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg f-body text-sm transition"
            style={{ background: active === it.key ? "rgba(34,211,238,0.1)" : "transparent", color: active === it.key ? C.cyan : C.muted }}>
            <it.icon size={17} className="flex-shrink-0" />
            {!collapsed && <span>{it.label}</span>}
          </button>
        ))}
      </nav>
      <div className="p-2 space-y-1" style={{ borderTop: `1px solid ${C.border}` }}>
        {!collapsed && (
          <div className="px-3 py-2 mb-1">
            <div className="f-body text-xs" style={{ color: C.text }}>{name}</div>
            <div className="f-body text-[11px]" style={{ color: C.muted }}>{roleLabel}</div>
          </div>
        )}
        <button onClick={onLogout} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg f-body text-sm" style={{ color: C.pulse }}>
          <LogOut size={17} /> {!collapsed && "Logout"}
        </button>
        <button onClick={() => setCollapsed(!collapsed)} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg f-body text-xs" style={{ color: C.muted2 }}>
          {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />} {!collapsed && "Collapse"}
        </button>
      </div>
    </div>
  );
}

function TopBar({ title, connected, lastUpdated, dark, setDark, notifCount = 0 }) {
  const [showNotif, setShowNotif] = useState(false);
  return (
    <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: `1px solid ${C.border}`, background: C.panel }}>
      <div>
        <h1 className="f-display font-semibold text-lg">{title}</h1>
        <div className="flex items-center gap-3 mt-0.5">
          <span className="inline-flex items-center gap-1 f-mono text-[11px]" style={{ color: C.muted }}>
            {connected ? <Wifi size={12} color={C.green} /> : <WifiOff size={12} color={C.pulse} />} ESP32 · <ConnDot connected={connected} />
          </span>
          <span className="f-mono text-[11px]" style={{ color: C.muted2 }}>Updated {lastUpdated}</span>
        </div>
      </div>
      <div className="flex items-center gap-3 relative">
        <button onClick={() => setDark(!dark)} className="p-2 rounded-lg" style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}` }}>
          {dark ? <Sun size={16} color={C.muted} /> : <Moon size={16} color={C.muted} />}
        </button>
        <button onClick={() => setShowNotif(!showNotif)} className="p-2 rounded-lg relative" style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}` }}>
          <Bell size={16} color={C.muted} />
          {notifCount > 0 && <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[9px] flex items-center justify-center f-mono" style={{ background: C.pulse, color: "#fff" }}>{notifCount}</span>}
        </button>
        <button className="p-2 rounded-lg" style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}` }}>
          <Settings size={16} color={C.muted} />
        </button>
      </div>
    </div>
  );
}

/* ============================== PLAYER DASHBOARD ============================== */
function PlayerDashboard({ tick, onLogout, name }) {
  const [active, setActive] = useState("overview");
  const [collapsed, setCollapsed] = useState(false);
  const [range, setRange] = useState("Today");
  const [dark, setDark] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [coachAdvice, setCoachAdvice] = useState("");
  const me = PLAYERS[0];
  const { data: t, history, source } = useLiveTelemetry(me.seed, me.fitnessBase, tick);
  const messages = useMemo(() => (t ? aiMessagesFor(t) : []), [t]);
  
  useEffect(() => {
  fetch("http://127.0.0.1:5000/api/sessions")
    .then((response) => response.json())
    .then((data) => {
      setSessions(data);
    })
    .catch((error) => {
      console.error("Error loading sessions:", error);
    });
}, []);
useEffect(() => {
  fetch("http://127.0.0.1:5000/api/sessions")
    .then((response) => response.json())
    .then((data) => {
      setSessions(data);
    })
    .catch((error) => {
      console.error("Error loading sessions:", error);
    });
}, []);

useEffect(() => {
  fetch("http://127.0.0.1:5000/api/coach")
    .then((response) => response.json())
    .then((data) => {
      setCoachAdvice(data.advice);
    })
    .catch((error) => {
      console.error("Error loading AI Coach:", error);
    });
}, []);
  if (!t) {
    return (
      <div className="min-h-screen flex items-center justify-center f-body" style={{ background: C.void, color: C.muted }}>
        <FontStyles />Connecting to sensors…
      </div>
    );
  }

  const items = [
    { key: "overview", label: "Overview", icon: Gauge },
    { key: "analytics", label: "Analytics", icon: BarChart3 },
    { key: "ai", label: "AI Coach", icon: Zap },
    { key: "achievements", label: "Achievements", icon: Award },
    {key: "video",label: "Video Analysis",icon: Video},
  ];

  return (
    <div className="min-h-screen flex f-body" style={{ background: C.void, color: C.text }}>
      <FontStyles />
      <Sidebar items={items} active={active} setActive={setActive} collapsed={collapsed} setCollapsed={setCollapsed}
        onLogout={onLogout} roleLabel="Player" name={name} />
      <div className="flex-1 min-w-0">
        <TopBar title={active === "overview" ? "Player Overview" : active === "analytics" ? "Performance Analytics" : active === "ai" ? "AI Coach" : "Achievements"}
          connected={true} lastUpdated="just now" dark={dark} setDark={setDark} notifCount={messages.filter(m => m.p !== "info").length} />
        <div className="px-6 pt-4">
  <span
    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] f-mono"
    style={{
      background: "rgba(52,211,153,0.12)",
      color: C.green,
    }}
  >
    <span
      className="w-1.5 h-1.5 rounded-full pulse-dot"
      style={{ background: C.green }}
    />
    CONNECTED — Flask Backend + AI Model
  </span>
</div>
        <div className="p-6 space-y-6 overflow-y-auto" style={{ maxHeight: "calc(100vh - 73px)" }}>

          {active === "overview" && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <GlassCard className="p-4 flex flex-col items-center">
                <Ring value={((t.hr > 0 ? t.hr : 78) / 190) * 100} color={C.pulse} label="Heart Rate" sub={`${t.hr > 0 ? t.hr : 78} BPM`}/></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={t.spo2} color={C.cyan} label="SpO₂" sub={`${t.spo2}%`} /></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={t.fatigue} color={C.amber} label="Fatigue" sub={`${t.fatigue}%`} /></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={t.performance} color={C.green} label="Performance" sub={`${t.performance}/100`} /></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={t.fitness} color={C.blue} label="Fitness Score" sub={`${t.fitness}/100`} /></GlassCard>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <GlassCard className="p-5 md:col-span-2">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="f-display font-semibold text-sm">Live Motion</h3>
                    <span className="px-2.5 py-1 rounded-full text-xs f-mono" style={{ background: `${C.blue}1A`, color: C.blue }}>{t.activity}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    {["x", "y", "z"].map((ax) => (
                      <div key={ax} className="p-3 rounded-lg" style={{ background: "rgba(255,255,255,0.03)" }}>
                        <div className="f-body text-[11px]" style={{ color: C.muted }}>Accel {ax.toUpperCase()}</div>
                        <div className="f-mono text-base font-semibold">{t.accel[ax]}</div>
                      </div>
                    ))}
                    {["x", "y", "z"].map((ax) => (
                      <div key={"g" + ax} className="p-3 rounded-lg" style={{ background: "rgba(255,255,255,0.03)" }}>
                        <div className="f-body text-[11px]" style={{ color: C.muted }}>Gyro {ax.toUpperCase()}</div>
                        <div className="f-mono text-base font-semibold">{t.gyro[ax]}°/s</div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
                <GlassCard className="p-5">
                  <h3 className="f-display font-semibold text-sm mb-3">Sensor Status</h3>
                  <div className="space-y-2.5 f-body text-sm">
                    <div className="flex justify-between">
                        <span style={{ color: C.muted }}>ESP32</span>
                        <ConnDot connected={t.sources?.wrist === "live"} />
                    </div>
                    <div className="flex justify-between">
                        <span style={{ color: C.muted }}>MPU6050</span>
                        <ConnDot connected={t.sources?.waist === "live"} />
                    </div>
                    <div className="flex justify-between">
                        <span style={{ color: C.muted }}>MAX30102</span>
                        <ConnDot connected={t.sources?.ankle === "live"} />
                    </div>
                        <span className="f-mono text-xs">{t.timestamp}</span>
                    </div>
                </GlassCard>
              </div>

              <GlassCard className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="f-display font-semibold text-sm">Heart Rate Trend</h3>
                  <div className="flex gap-1">
                    {["Today", "Last 7 Days", "Last 30 Days", "Custom"].map((r) => (
                      <button key={r} onClick={() => setRange(r)} className="px-2.5 py-1 rounded-full text-[11px] f-body"
                        style={{ background: range === r ? C.cyan : "rgba(255,255,255,0.05)", color: range === r ? "#04121A" : C.muted }}>{r}</button>
                    ))}
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={history}>
                    <defs>
                      <linearGradient id="hrGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={C.pulse} stopOpacity={0.4} />
                        <stop offset="100%" stopColor={C.pulse} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
                    <XAxis dataKey="t" stroke={C.muted2} fontSize={10} tickLine={false} />
                    <YAxis stroke={C.muted2} fontSize={10} tickLine={false} domain={["auto", "auto"]} />
                    <Tooltip contentStyle={{ background: C.panel2, border: `1px solid ${C.border}`, borderRadius: 8, fontSize: 12 }} />
                    <Area type="monotone" dataKey="hr" stroke={C.pulse} fill="url(#hrGrad)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </GlassCard>
            </>
          )}

          {active === "analytics" && (
            <>
              <div className="grid md:grid-cols-2 gap-4">
                <GlassCard className="p-5">
                  <h3 className="f-display font-semibold text-sm mb-3">SpO₂ Trend</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
                      <XAxis dataKey="t" stroke={C.muted2} fontSize={10} />
                      <YAxis stroke={C.muted2} fontSize={10} domain={[90, 100]} />
                      <Tooltip contentStyle={{ background: C.panel2, border: `1px solid ${C.border}`, borderRadius: 8, fontSize: 12 }} />
                      <Line type="monotone" dataKey="spo2" stroke={C.cyan} strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </GlassCard>
                <GlassCard className="p-5">
                  <h3 className="f-display font-semibold text-sm mb-3">Movement Intensity</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
                      <XAxis dataKey="t" stroke={C.muted2} fontSize={10} />
                      <YAxis stroke={C.muted2} fontSize={10} />
                      <Tooltip contentStyle={{ background: C.panel2, border: `1px solid ${C.border}`, borderRadius: 8, fontSize: 12 }} />
                      <Bar dataKey="movement" fill={C.blue} radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </GlassCard>
              </div>

              <GlassCard className="p-5">
                <h3 className="f-display font-semibold text-sm mb-4">Session History</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm f-body">
                   <thead>
  <tr style={{ color: C.muted, borderBottom: `1px solid ${C.border}` }}>
    {[
      "Date & Time",
      "Activity",
      "Heart Rate",
      "SpO₂",
      "Fatigue",
      "Performance",
      "Steps",
    ].map((h) => (
      <th key={h} className="text-left py-2 font-medium text-xs">
        {h}
      </th>
    ))}
  </tr>
</thead>
                    <tbody>
  {sessions.map((s) => (
    <tr key={s.id} style={{ borderBottom: `1px solid ${C.border}` }}>
      <td>{new Date(s.timestamp).toLocaleString()}</td>
      <td>{s.activity}</td>
      <td>{s.heart_rate} BPM</td>
      <td>{s.spo2}%</td>
      <td>{s.fatigue}%</td>
      <td>{s.performance}</td>
      <td>{s.steps}</td>
    </tr>
  ))}
</tbody>
                  </table>
                </div>
              </GlassCard>
            </>
          )}

          {active === "ai" && (
  <GlassCard className="p-6">
    <h2
      className="f-display text-xl font-semibold mb-4"
      style={{ color: C.cyan }}
    >
      🤖 Gemini AI Coach
    </h2>

    <div
      className="f-body text-sm whitespace-pre-wrap"
      style={{
        color: C.text,
        lineHeight: "1.8",
      }}
    >
      {coachAdvice
  ? coachAdvice.split("\n").map((line, index) => (
      <p key={index} style={{ marginBottom: "12px" }}>
        {line}
      </p>
    ))
  : "Loading AI coaching advice..."}
    </div>
  </GlassCard>
)}

{active === "video" && (
  <VideoAnalysis />
)}

          {active === "achievements" && (
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              {BADGES.map((b, i) => (
                <GlassCard key={i} className="p-5 flex items-start gap-3" style={{ opacity: b.earned ? 1 : 0.5 }}>
                  <div className="p-2.5 rounded-lg" style={{ background: b.earned ? `${C.cyan}1A` : "rgba(255,255,255,0.04)" }}>
                    {b.earned ? <b.icon size={18} color={C.cyan} /> : <Lock size={18} color={C.muted2} />}
                  </div>
                  <div>
                    <h4 className="f-display font-semibold text-sm">{b.name}</h4>
                    <p className="f-body text-xs mt-1" style={{ color: C.muted }}>{b.desc}</p>
                  </div>
                </GlassCard>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ============================== COACH DASHBOARD ============================== */
function CoachDashboard({ tick, onLogout, name }) {
  const [active, setActive] = useState("overview");
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(true);
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState("performance");
  const [selected, setSelected] = useState(null);

  const withTelemetry = useMemo(() => PLAYERS.map((p) => ({ ...p, t: telemetryAt(p.seed, tick, p.fitnessBase), online: p.seed % 5 !== 0 })), [tick]);

  const filtered = useMemo(() => {
    let arr = withTelemetry.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()));
    arr.sort((a, b) => {
      if (sortBy === "performance") return b.t.performance - a.t.performance;
      if (sortBy === "fitness") return b.t.fitness - a.t.fitness;
      if (sortBy === "fatigue") return b.t.fatigue - a.t.fatigue;
      return 0;
    });
    return arr;
  }, [withTelemetry, query, sortBy]);

  const alerts = useMemo(() => withTelemetry.flatMap((p) => {
    const a = [];
    if (p.t.hr > 165) a.push({ p: p.name, text: `Abnormal heart rate: ${p.t.hr} BPM`, level: "critical" });
    if (p.t.spo2 < 94) a.push({ p: p.name, text: `Low SpO₂: ${p.t.spo2}%`, level: "critical" });
    if (!p.online) a.push({ p: p.name, text: `Inactive / device offline`, level: "warning" });
    return a;
  }), [withTelemetry]);

  const teamAvgHr = Math.round(withTelemetry.reduce((s, p) => s + p.t.hr, 0) / withTelemetry.length);
  const teamAvgSpo2 = Math.round((withTelemetry.reduce((s, p) => s + p.t.spo2, 0) / withTelemetry.length) * 10) / 10;
  const teamPerf = Math.round(withTelemetry.reduce((s, p) => s + p.t.performance, 0) / withTelemetry.length);
  const teamFatigue = Math.round(withTelemetry.reduce((s, p) => s + p.t.fatigue, 0) / withTelemetry.length);
  const activeCount = withTelemetry.filter((p) => p.online).length;

  const items = [
    { key: "overview", label: "Overview", icon: Gauge },
    { key: "players", label: "Players", icon: Users },
    { key: "leaderboard", label: "Leaderboard", icon: Trophy },
    { key: "alerts", label: "Alerts", icon: Bell },
  ];

  if (selected) {
    const p = withTelemetry.find((x) => x.id === selected);
    const hist = Array.from({ length: 24 }, (_, i) => {
      const tt = tick - (23 - i);
      const h = telemetryAt(p.seed, tt, p.fitnessBase);
      return { t: `${i}`, hr: h.hr, spo2: h.spo2, movement: h.movement, gyro: Math.abs(h.gyro.x) };
    });
    const msgs = aiMessagesFor(p.t);
    return (
      <div className="min-h-screen flex f-body" style={{ background: C.void, color: C.text }}>
        <FontStyles />
        <Sidebar items={items} active={active} setActive={(k) => { setSelected(null); setActive(k); }} collapsed={collapsed} setCollapsed={setCollapsed}
          onLogout={onLogout} roleLabel="Coach" name={name} />
        <div className="flex-1 min-w-0">
          <TopBar title={`${p.name} · #${p.jersey}`} connected={p.online} lastUpdated="just now" dark={dark} setDark={setDark} />
          <div className="p-6 space-y-6 overflow-y-auto" style={{ maxHeight: "calc(100vh - 73px)" }}>
            <button onClick={() => setSelected(null)} className="flex items-center gap-1 f-body text-sm" style={{ color: C.cyan }}>
              <ChevronLeft size={15} /> Back to players
            </button>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <GlassCard className="p-4 flex flex-col items-center"><Ring value={(p.t.hr / 190) * 100} color={C.pulse} label="Heart Rate" sub={`${p.t.hr} BPM`} /></GlassCard>
              <GlassCard className="p-4 flex flex-col items-center"><Ring value={p.t.spo2} color={C.cyan} label="SpO₂" sub={`${p.t.spo2}%`} /></GlassCard>
              <GlassCard className="p-4 flex flex-col items-center"><Ring value={p.t.fatigue} color={C.amber} label="Fatigue" sub={`${p.t.fatigue}%`} /></GlassCard>
              <GlassCard className="p-4 flex flex-col items-center"><Ring value={p.t.performance} color={C.green} label="Performance" sub={`${p.t.performance}/100`} /></GlassCard>
              <GlassCard className="p-4 flex flex-col items-center"><Ring value={p.t.fitness} color={C.blue} label="Fitness" sub={`${p.t.fitness}/100`} /></GlassCard>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <GlassCard className="p-5">
                <h3 className="f-display font-semibold text-sm mb-3">Heart Rate Trend</h3>
                <ResponsiveContainer width="100%" height={170}>
                  <AreaChart data={hist}>
                    <defs><linearGradient id="hrGrad2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.pulse} stopOpacity={0.4} /><stop offset="100%" stopColor={C.pulse} stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
                    <XAxis dataKey="t" stroke={C.muted2} fontSize={10} /><YAxis stroke={C.muted2} fontSize={10} />
                    <Tooltip contentStyle={{ background: C.panel2, border: `1px solid ${C.border}`, borderRadius: 8, fontSize: 12 }} />
                    <Area type="monotone" dataKey="hr" stroke={C.pulse} fill="url(#hrGrad2)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </GlassCard>
              <GlassCard className="p-5">
                <h3 className="f-display font-semibold text-sm mb-3">SpO₂ &amp; Movement</h3>
                <ResponsiveContainer width="100%" height={170}>
                  <LineChart data={hist}>
                    <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
                    <XAxis dataKey="t" stroke={C.muted2} fontSize={10} /><YAxis stroke={C.muted2} fontSize={10} />
                    <Tooltip contentStyle={{ background: C.panel2, border: `1px solid ${C.border}`, borderRadius: 8, fontSize: 12 }} />
                    <Line type="monotone" dataKey="spo2" stroke={C.cyan} strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="movement" stroke={C.blue} strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </GlassCard>
            </div>
            <GlassCard className="p-5">
              <h3 className="f-display font-semibold text-sm mb-3">Activity Timeline</h3>
              <div className="flex items-center gap-4 f-body text-sm" style={{ color: C.muted }}>
                <span className="flex items-center gap-1.5"><Clock size={14} /> Session duration: 42 min</span>
                <span>Current: <b style={{ color: C.text }}>{p.t.activity}</b></span>
                <span>Fatigue: <b style={{ color: p.t.fatigue > 70 ? C.pulse : C.text }}>{p.t.fatigue}%</b></span>
              </div>
            </GlassCard>
            <div className="space-y-3">
              <h3 className="f-display font-semibold text-sm">AI Recommendations for {p.name.split(" ")[0]}</h3>
              {msgs.map((m, i) => (
                <GlassCard key={i} className="p-4 flex gap-3 items-start">
                  <div className="p-2 rounded-lg flex-shrink-0" style={{ background: "rgba(255,255,255,0.05)" }}><m.icon size={16} /></div>
                  <div><PriorityBadge p={m.p} /><p className="f-body text-sm mt-2">{m.text}</p></div>
                </GlassCard>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex f-body" style={{ background: C.void, color: C.text }}>
      <FontStyles />
      <Sidebar items={items} active={active} setActive={setActive} collapsed={collapsed} setCollapsed={setCollapsed}
        onLogout={onLogout} roleLabel="Coach" name={name} />
      <div className="flex-1 min-w-0">
        <TopBar title={active === "overview" ? "Team Overview" : active === "players" ? "Players" : active === "leaderboard" ? "Leaderboard" : "Alerts"}
          connected={true} lastUpdated="just now" dark={dark} setDark={setDark} notifCount={alerts.length} />
        <div className="p-6 space-y-6 overflow-y-auto" style={{ maxHeight: "calc(100vh - 73px)" }}>

          {active === "overview" && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatChip icon={Users} label="Total Players" value={PLAYERS.length} unit="" color={C.blue} />
                <StatChip icon={Radio} label="Active Players" value={activeCount} unit="" color={C.green} />
                <StatChip icon={Wifi} label="Connected Devices" value={activeCount} unit="" color={C.cyan} />
                <StatChip icon={Play} label="Live Sessions" value={activeCount} unit="" color={C.amber} />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={(teamAvgHr / 190) * 100} color={C.pulse} label="Avg Team HR" sub={`${teamAvgHr} BPM`} /></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={teamAvgSpo2} color={C.cyan} label="Avg Team SpO₂" sub={`${teamAvgSpo2}%`} /></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={teamPerf} color={C.green} label="Team Performance" sub={`${teamPerf}/100`} /></GlassCard>
                <GlassCard className="p-4 flex flex-col items-center"><Ring value={teamFatigue} color={C.amber} label="Team Fatigue" sub={`${teamFatigue}%`} /></GlassCard>
              </div>
              <GlassCard className="p-5">
                <h3 className="f-display font-semibold text-sm mb-4">Team Roster</h3>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {withTelemetry.slice(0, 6).map((p) => (
                    <button key={p.id} onClick={() => setSelected(p.id)} className="text-left p-3 rounded-xl transition hover:opacity-90" style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${C.border}` }}>
                      <div className="flex items-center justify-between">
                        <span className="f-body text-sm font-medium">{p.name}</span>
                        <ConnDot connected={p.online} />
                      </div>
                      <div className="flex items-center gap-3 mt-1.5 f-mono text-xs" style={{ color: C.muted }}>
                        <span className="flex items-center gap-1"><Heart size={11} color={C.pulse} />{p.t.hr}</span>
                        <span className="flex items-center gap-1"><Wind size={11} color={C.cyan} />{p.t.spo2}%</span>
                      </div>
                    </button>
                  ))}
                </div>
              </GlassCard>
            </>
          )}

          {active === "players" && (
            <>
              <div className="flex flex-wrap items-center gap-3">
                <div className="relative flex-1 min-w-[200px]">
                  <Search size={15} className="absolute left-3 top-2.5" color={C.muted} />
                  <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search players..."
                    className="w-full pl-9 pr-3 py-2 rounded-lg f-body text-sm outline-none" style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${C.border}`, color: C.text }} />
                </div>
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="px-3 py-2 rounded-lg f-body text-sm outline-none"
                  style={{ background: C.panel2, border: `1px solid ${C.border}`, color: C.text }}>
                  <option value="performance">Sort: Performance</option>
                  <option value="fitness">Sort: Fitness</option>
                  <option value="fatigue">Sort: Fatigue</option>
                </select>
                {["All", "Idle", "Walking", "Running", "Sprinting"].map((f) => (
                  <span key={f} className="px-2.5 py-1 rounded-full text-[11px] f-body" style={{ background: "rgba(255,255,255,0.04)", color: C.muted, border: `1px solid ${C.border}` }}>{f}</span>
                ))}
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filtered.map((p) => (
                  <GlassCard key={p.id} className="p-5 cursor-pointer transition hover:opacity-95" style={{}}>
                    <div onClick={() => setSelected(p.id)}>
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="f-display font-semibold text-sm">{p.name}</h4>
                          <p className="f-body text-xs" style={{ color: C.muted }}>#{p.jersey} · {p.position}</p>
                        </div>
                        <ConnDot connected={p.online} />
                      </div>
                      <div className="grid grid-cols-2 gap-2 mt-4">
                        <div className="flex items-center gap-1.5 f-mono text-sm"><Heart size={13} color={C.pulse} />{p.t.hr} BPM</div>
                        <div className="flex items-center gap-1.5 f-mono text-sm"><Wind size={13} color={C.cyan} />{p.t.spo2}%</div>
                        <div className="flex items-center gap-1.5 f-body text-xs" style={{ color: C.muted }}><Activity size={13} />{p.t.activity}</div>
                        <div className="flex items-center gap-1.5 f-body text-xs" style={{ color: C.muted }}><Gauge size={13} />Perf {p.t.performance}</div>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-3" style={{ borderTop: `1px solid ${C.border}` }}>
                        <span className="f-body text-xs" style={{ color: C.muted }}>Fitness {p.t.fitness}/100</span>
                        <ChevronRight size={14} color={C.muted} />
                      </div>
                    </div>
                  </GlassCard>
                ))}
              </div>
            </>
          )}

          {active === "leaderboard" && (
            <GlassCard className="p-5">
              <h3 className="f-display font-semibold text-sm mb-4">Leaderboard · Performance Score</h3>
              <div className="space-y-2">
                {[...withTelemetry].sort((a, b) => b.t.performance - a.t.performance).map((p, i) => (
                  <div key={p.id} onClick={() => setSelected(p.id)} className="flex items-center gap-4 p-3 rounded-xl cursor-pointer" style={{ background: i < 3 ? "rgba(34,211,238,0.06)" : "rgba(255,255,255,0.02)" }}>
                    <span className="f-mono text-sm w-6" style={{ color: i === 0 ? C.amber : C.muted }}>{i + 1}</span>
                    <span className="flex-1 f-body text-sm">{p.name}</span>
                    <span className="f-body text-xs" style={{ color: C.muted }}>#{p.jersey}</span>
                    <span className="f-mono text-sm font-semibold" style={{ color: C.green }}>{p.t.performance}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {active === "alerts" && (
            <div className="space-y-3 max-w-2xl">
              {alerts.length === 0 && <GlassCard className="p-6 text-center f-body text-sm" style={{ color: C.muted }}>No active alerts — the whole team looks steady.</GlassCard>}
              {alerts.map((a, i) => (
                <GlassCard key={i} className="p-4 flex items-center gap-3">
                  <div className="p-2 rounded-lg" style={{ background: a.level === "critical" ? "rgba(251,113,133,0.12)" : "rgba(251,191,36,0.12)" }}>
                    <AlertTriangle size={16} color={a.level === "critical" ? C.pulse : C.amber} />
                  </div>
                  <div className="flex-1">
                    <span className="f-body text-sm font-medium">{a.p}</span>
                    <p className="f-body text-xs" style={{ color: C.muted }}>{a.text}</p>
                  </div>
                  <PriorityBadge p={a.level} />
                </GlassCard>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ============================== ROOT APP ============================== */
export default function App() {
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [tick, setTick] = useState(Math.floor(Date.now() / 1000 / 2));

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 2000);
    return () => clearInterval(id);
  }, []);

  const handleLogin = (role) => {
    setSession({
      role,
      name: role === "player" ? "Alex Carter" : "Coach Delgado",
    });

    navigate(role === "player" ? "/player" : "/coach");
  };

  const handleLogout = () => {
    setSession(null);
    navigate("/");
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Landing
            onGetStarted={() => navigate("/login")}
          />
        }
      />

      <Route
        path="/login"
        element={
          <LoginPage
            onLogin={handleLogin}
            onBack={() => navigate("/")}
          />
        }
      />

      <Route
        path="/player"
        element={
          session?.role === "player" ? (
            <PlayerDashboard
              tick={tick}
              onLogout={handleLogout}
              name={session?.name}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      <Route
        path="/coach"
        element={
          session?.role === "coach" ? (
            <CoachDashboard
              tick={tick}
              onLogout={handleLogout}
              name={session?.name}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
}