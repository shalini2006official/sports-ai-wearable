function HistoryCard({ session }) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: "10px",
        padding: "15px",
        marginBottom: "15px",
      }}
    >
      <h3>Workout #{session.id}</h3>

      <p><b>Time:</b> {session.timestamp}</p>
      <p><b>Activity:</b> {session.activity}</p>
      <p><b>Heart Rate:</b> {session.heart_rate} BPM</p>
      <p><b>SpO₂:</b> {session.spo2}%</p>
      <p><b>Fatigue:</b> {session.fatigue}</p>
      <p><b>Performance:</b> {session.performance}</p>
      <p><b>Posture:</b> {session.posture}</p>
      <p><b>Steps:</b> {session.steps}</p>
      <p><b>Cadence:</b> {session.cadence}</p>
      <p><b>Stride Length:</b> {session.stride_length}</p>
      <p><b>Temperature:</b> {session.temperature}°C</p>
    </div>
  );
}

export default HistoryCard;