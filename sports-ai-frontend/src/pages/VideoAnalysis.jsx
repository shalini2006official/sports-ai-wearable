import { useState } from "react";
console.log("VideoAnalysis component loaded");
export default function VideoAnalysis() {

  const [video, setVideo] = useState(null);

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleVideo = (e) => {
    setVideo(e.target.files[0]);
  };

  const uploadVideo = async () => {

    console.log("1. Upload button clicked");

    if (!video) {
        alert("Select a video first");
        return;
    }
    setLoading(true);
    setMessage("");
    try {

        console.log("2. Creating FormData");

        const formData = new FormData();

        formData.append("video", video);

        console.log("3. Sending request...");

        const response = await fetch(
            "http://127.0.0.1:5000/api/video",
            {
                method: "POST",
                body: formData,
            }
        );

        console.log("4. Status:", response.status);

        const data = await response.json();

        console.log("5. Response:", data);

        alert(data.message);

        setMessage(data.analysis);

    } catch (error) {

        console.error("UPLOAD ERROR:", error);

        alert(error);

    }
    finally {

        setLoading(false);

    }
};

  return (
  <div style={{ padding: "30px", color: "white", maxWidth: "900px" }}>

    <h1 style={{ color: "#22d3ee", fontSize: "34px" }}>
      🎥 AI Video Analysis
    </h1>

    <p style={{ color: "#94a3b8", marginBottom: "25px" }}>
      Upload your sports performance video and let AI analyze your movement,
      posture, balance, injury risk and provide coaching feedback.
    </p>

    <div
      style={{
        border: "2px dashed #22d3ee",
        borderRadius: "15px",
        padding: "40px",
        textAlign: "center",
        background: "#111827",
      }}
    >
      <input
        type="file"
        accept="video/*"
        onChange={handleVideo}
      />

      <br />
      <br />

      {video && (
        <div style={{ color: "#22d3ee", fontWeight: "bold" }}>
          ✅ {video.name}
        </div>
      )}
    </div>

    <br />

    <button
      onClick={uploadVideo}
      style={{
        width: "100%",
        background: "#06b6d4",
        color: "white",
        border: "none",
        padding: "16px",
        borderRadius: "10px",
        cursor: "pointer",
        fontSize: "18px",
        fontWeight: "bold",
      }}
    >
      🚀 Analyze Video
    </button>

    <br />
    <br />

    {video && (
      <video
        width="100%"
        controls
        src={URL.createObjectURL(video)}
        style={{
          borderRadius: "15px",
          marginBottom: "25px",
        }}
      />
    )}

    {loading && (
  <div
    style={{
      background: "#1f2937",
      padding: "25px",
      borderRadius: "15px",
      textAlign: "center",
      marginTop: "20px",
    }}
  >
    <h2 style={{ color: "#22d3ee" }}>
      🔄 AI is analyzing your performance...
    </h2>

    <p style={{ color: "#9ca3af" }}>
      Please wait a few seconds.
    </p>
  </div>
)}

{message && (
  <div
    style={{
      background: "#1f2937",
      padding: "25px",
      borderRadius: "15px",
      whiteSpace: "pre-wrap",
      lineHeight: "1.8",
      border: "1px solid #374151",
      marginTop: "20px",
    }}
  >
    <h2 style={{ color: "#22d3ee" }}>
      🤖 AI Coach Analysis
    </h2>

    <hr />

    {message}
  </div>
)}



{/* ADD THIS HERE */}

{message && (
  <button
    onClick={() =>
      window.open("http://127.0.0.1:5000/api/report", "_blank")
    }
    style={{
      marginTop: "20px",
      background: "#22c55e",
      color: "white",
      padding: "12px 20px",
      border: "none",
      borderRadius: "10px",
      cursor: "pointer",
      fontWeight: "bold",
      width: "100%",
    }}
  >
    📄 Download AI Report
  </button>
)}

  </div>
);
}