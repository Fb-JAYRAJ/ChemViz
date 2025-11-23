// Sidebar navigation for scrolling to sections
import React from "react";
import "./sidebar.css";

export default function Sidebar() {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">ChemViz</h2>

      <nav className="sidebar-menu">
        <div className="sidebar-item" onClick={() => scrollTo("dashboard")}>Dashboard</div>
        <div className="sidebar-item" onClick={() => scrollTo("upload")}>Upload</div>
        <div className="sidebar-item" onClick={() => scrollTo("history")}>History</div>
        <div className="sidebar-item" onClick={() => scrollTo("charts")}>Charts</div>
      </nav>

      <div className="version">v1.0</div>
    </aside>
  );
}