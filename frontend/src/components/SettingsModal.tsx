import { useEffect, useState } from "react";

interface Settings {
    apiUrl: string;
    apiKey: string;
}

function loadSettings(): Settings {
    const stored = localStorage.getItem("rag_settings");
    const parsed = stored ? JSON.parse(stored) : {};
    return {
        apiUrl: parsed.apiUrl ?? "",
        apiKey: parsed.apiKey ?? "dev-secret-change-me",
    };
}

interface Props {
    onClose: () => void;
}

export function SettingsModal({ onClose }: Props) {
    const [settings, setSettings] = useState<Settings>(loadSettings);

    // Close on Escape
    useEffect(() => {
        const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
    }, [onClose]);

    const handleSave = () => {
        localStorage.setItem("rag_settings", JSON.stringify(settings));
        onClose();
    };

    return (
        <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="modal" role="dialog" aria-label="Settings">
                <div className="modal-header">
                    <span className="modal-title">⚙ Settings</span>
                    <button className="modal-close" onClick={onClose} aria-label="Close settings">✕</button>
                </div>

                <div className="form-group">
                    <label className="form-label" htmlFor="api-url-input">API Base URL</label>
                    <input
                        id="api-url-input"
                        className="form-input"
                        type="url"
                        placeholder="http://localhost:8000 (leave blank for dev proxy)"
                        value={settings.apiUrl}
                        onChange={(e) => setSettings((s) => ({ ...s, apiUrl: e.target.value }))}
                    />
                    <span className="form-hint">Leave blank when using the Vite dev proxy.</span>
                </div>

                <div className="form-group">
                    <label className="form-label" htmlFor="api-key-input">API Key</label>
                    <input
                        id="api-key-input"
                        className="form-input"
                        type="password"
                        placeholder="X-API-Key value"
                        value={settings.apiKey}
                        onChange={(e) => setSettings((s) => ({ ...s, apiKey: e.target.value }))}
                    />
                    <span className="form-hint">Matches the API_KEY set in backend .env</span>
                </div>

                <div className="modal-actions">
                    <button className="btn-secondary" onClick={onClose} id="settings-cancel-btn">Cancel</button>
                    <button className="btn-primary" onClick={handleSave} id="settings-save-btn">Save</button>
                </div>
            </div>
        </div>
    );
}
