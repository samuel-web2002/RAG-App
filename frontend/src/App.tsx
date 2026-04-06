import { useState } from "react";
import "./index.css";
import { ChatWindow } from "./components/ChatWindow";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { SettingsModal } from "./components/SettingsModal";

type View = "chat" | "documents";

const NAV_ITEMS: Array<{ id: View; label: string; icon: string }> = [
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "documents", label: "Documents", icon: "📚" },
];

export default function App() {
  const [view, setView] = useState<View>("chat");
  const [showSettings, setShowSettings] = useState(false);
  const sessionId = "default";

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">✦</div>
          <span className="sidebar-logo-text">RAG Chatbot</span>
        </div>

        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            id={`nav-${item.id}`}
            className={`sidebar-nav-item${view === item.id ? " active" : ""}`}
            onClick={() => setView(item.id)}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </button>
        ))}

        <div className="sidebar-spacer" />

        <button
          id="settings-btn"
          className="sidebar-settings-btn"
          onClick={() => setShowSettings(true)}
        >
          ⚙ Settings
        </button>
      </aside>

      {/* Main content */}
      <main className="main-content">
        {view === "chat" && <ChatWindow sessionId={sessionId} />}
        {view === "documents" && <DocumentsPanel />}
      </main>

      {/* Settings modal */}
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </div>
  );
}
