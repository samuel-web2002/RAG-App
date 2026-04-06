import { useCallback, useEffect, useRef, useState } from "react";
import type { DocumentInfo } from "../types/api";
import { deleteDocument, ingestDocument, listDocuments } from "../api/client";

const ICON_MAP: Record<string, string> = {
    pdf: "📄",
    txt: "📝",
    md: "📋",
};

function docIcon(filename: string): string {
    const ext = filename.split(".").pop()?.toLowerCase() ?? "";
    return ICON_MAP[ext] ?? "📁";
}

export function DocumentsPanel() {
    const [docs, setDocs] = useState<DocumentInfo[]>([]);
    const [uploading, setUploading] = useState(false);
    const [dragging, setDragging] = useState(false);
    const [toast, setToast] = useState<{ type: "success" | "error"; msg: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const showToast = (type: "success" | "error", msg: string) => {
        setToast({ type, msg });
        setTimeout(() => setToast(null), 4000);
    };

    const fetchDocs = useCallback(async () => {
        try {
            const res = await listDocuments();
            setDocs(res.documents);
        } catch {
            /* silent on initial load */
        }
    }, []);

    useEffect(() => { fetchDocs(); }, [fetchDocs]);

    const handleUpload = async (file: File) => {
        setUploading(true);
        try {
            const res = await ingestDocument(file);
            showToast("success", `${res.filename} — ${res.chunks_created} chunks indexed`);
            await fetchDocs();
        } catch (err) {
            showToast("error", err instanceof Error ? err.message : "Upload failed");
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleUpload(file);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleUpload(file);
        e.target.value = "";
    };

    const handleDelete = async (doc: DocumentInfo) => {
        try {
            await deleteDocument(doc.id);
            showToast("success", `"${doc.filename}" removed`);
            setDocs((prev) => prev.filter((d) => d.id !== doc.id));
        } catch (err) {
            showToast("error", err instanceof Error ? err.message : "Delete failed");
        }
    };

    return (
        <div className="docs-view">
            <div className="docs-header">
                <h1>Documents</h1>
                <p>Upload PDF, TXT, or Markdown files to build your knowledge base.</p>
            </div>

            {/* Drop zone */}
            <div
                className={`drop-zone${dragging ? " dragging" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                id="drop-zone"
            >
                <div className="drop-zone-icon">☁</div>
                <p className="drop-zone-title">Drag & drop a file here</p>
                <p className="drop-zone-subtitle">Supports PDF, TXT, Markdown · Max 50 MB</p>
                <button className="upload-btn" type="button" id="upload-btn">
                    Browse Files
                </button>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.txt,.md"
                    style={{ display: "none" }}
                    onChange={handleFileChange}
                    id="file-input"
                />
            </div>

            {/* Progress / Toast */}
            {uploading && (
                <div className="upload-progress">
                    <div className="progress-spinner" />
                    Indexing document…
                </div>
            )}
            {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}

            {/* Document list */}
            <div>
                <p className="docs-section-title" style={{ marginBottom: "10px" }}>
                    Indexed Documents ({docs.length})
                </p>
                <div className="docs-list">
                    {docs.length === 0 ? (
                        <div className="docs-empty">
                            No documents yet. Upload your first file to get started.
                        </div>
                    ) : (
                        docs.map((doc) => (
                            <div key={doc.id} className="doc-card">
                                <div className="doc-icon">{docIcon(doc.filename)}</div>
                                <div className="doc-info">
                                    <p className="doc-name">{doc.filename}</p>
                                    <p className="doc-meta">{doc.chunk_count} chunks · {doc.id.slice(0, 8)}…</p>
                                </div>
                                <button
                                    className="doc-delete-btn"
                                    onClick={() => handleDelete(doc)}
                                    title="Delete document"
                                    aria-label={`Delete ${doc.filename}`}
                                >
                                    🗑
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
