// Main React app for ChemViz (CSV upload → analysis → charts)
import React, { useState } from "react";
import axios from "axios";
import Sidebar from "./components/sidebar";
import "./index.css";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const [currentDataset, setCurrentDataset] = useState(null);
  const [history, setHistory] = useState([]);

  const authHeaders = () => ({
    Authorization: "Basic " + btoa(`${username}:${password}`),
  });

  // Upload CSV to backend
  const handleUpload = async () => {
    if (!username || !password) return alert("Enter credentials");
    if (!file) return alert("Select a CSV");

    setIsUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);

      const res = await axios.post(`${API_BASE}/api/upload/`, fd, {
        headers: { ...authHeaders(), "Content-Type": "multipart/form-data" },
      });

      setCurrentDataset(res.data);
      fetchHistory();
      alert("Uploaded");
    } catch {
      alert("Upload failed");
    }
    setIsUploading(false);
  };

  // Load latest summary
  const loadLatestSummary = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/summary/latest/`, {
        headers: authHeaders(),
      });
      setCurrentDataset(res.data);
      fetchHistory();
    } catch {
      alert("Could not load summary");
    }
  };

  // Fetch history list
  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/history/`, {
        headers: authHeaders(),
      });
      setHistory(res.data);
    } catch {}
  };

  // Download PDF
  const downloadPdf = async () => {
    if (!currentDataset) return alert("No dataset");

    try {
      const resp = await axios.get(
        `${API_BASE}/api/report/${currentDataset.id}/`,
        { headers: authHeaders(), responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([resp.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "report.pdf");
      link.click();
    } catch {
      alert("PDF failed");
    }
  };

  // Chart data
  const pieData = currentDataset
    ? {
        labels: Object.keys(currentDataset.type_distribution || {}),
        datasets: [
          {
            data: Object.values(currentDataset.type_distribution || {}),
            backgroundColor: ["#60A5FA", "#34D399", "#F472B6", "#FBBF24", "#A78BFA", "#F87171"],
          },
        ],
      }
    : null;

  const barData = currentDataset
    ? {
        labels: ["Flowrate", "Pressure", "Temperature"],
        datasets: [
          {
            label: "Average",
            data: [
              currentDataset.avg_flowrate,
              currentDataset.avg_pressure,
              currentDataset.avg_temperature,
            ],
            backgroundColor: ["#3B82F6", "#EF4444", "#10B981"],
            borderRadius: 6,
          },
        ],
      }
    : null;

  return (
    <div className="app-wrap">
      <Sidebar />

      <main className="main">
        <div id="dashboard">
          <h1 className="title">ChemViz – Chemical Data Visualizer</h1>
        </div>

        {/* Upload */}
        <div id="upload" className="card">
          <h2>1. Upload CSV</h2>

          <div className="grid-2">
            <div>
              <label>Username</label>
              <input
                className="input"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div>
              <label>Password</label>
              <input
                className="input"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <label>Select CSV file</label>
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />

          <div className="btn-row">
            <button className="btn blue" onClick={handleUpload}>
              {isUploading ? "Uploading..." : "Upload & Analyse"}
            </button>
            <button className="btn gray" onClick={loadLatestSummary}>Load Latest Summary</button>
            <button className="btn green" onClick={downloadPdf}>Download PDF Report</button>
          </div>
        </div>

        {/* Summary */}
        <div id="summary" className="card">
          <h2>2. Summary</h2>

          {!currentDataset ? (
            <p>No dataset selected.</p>
          ) : (
            <div className="summary-grid">
              <div className="summary-box">
                <div className="summary-label">Total Count</div>
                <div className="summary-value">{currentDataset.total_count}</div>
              </div>

              <div className="summary-box">
                <div className="summary-label">Avg Flowrate</div>
                <div className="summary-value">{currentDataset.avg_flowrate.toFixed(2)}</div>
              </div>

              <div className="summary-box">
                <div className="summary-label">Avg Pressure</div>
                <div className="summary-value">{currentDataset.avg_pressure.toFixed(2)}</div>
              </div>

              <div className="summary-box">
                <div className="summary-label">Avg Temperature</div>
                <div className="summary-value">{currentDataset.avg_temperature.toFixed(2)}</div>
              </div>
            </div>
          )}
        </div>

        {/* Charts */}
        <div id="charts" className="charts-grid">
          <div className="card">
            <h3>Type Distribution</h3>
            {pieData ? <Pie data={pieData} /> : <p>No data</p>}
          </div>

          <div className="card chart-full">
            <h3>Average Parameters</h3>
            {barData ? <Bar data={barData} /> : <p>No data</p>}
          </div>
        </div>

        {/* History */}
        <div id="history" className="card">
          <h2>3. History</h2>

          <button className="btn gray" onClick={fetchHistory}>Refresh</button>

          {history.length === 0 ? (
            <p>No history yet.</p>
          ) : (
            history.map((h) => (
              <div className="history-item" key={h.id}>
                <div>
                  <b>{h.name}</b><br />
                  <span>{new Date(h.created_at).toLocaleString()}</span>
                </div>

                <button className="btn gray" onClick={() => setCurrentDataset(h)}>
                  View
                </button>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

export default App;