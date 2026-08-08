import { useEffect, useState } from "react";
import HistoryCard from "../components/HistoryCard";

const API = "http://localhost:5000/api/sessions";

function History() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    fetch(API)
      .then((res) => res.json())
      .then((data) => setSessions(data))
      .catch((err) => console.log(err));
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Workout History</h1>

      {sessions.map((session) => (
        <HistoryCard key={session.id} session={session} />
      ))}
    </div>
  );
}

export default History;