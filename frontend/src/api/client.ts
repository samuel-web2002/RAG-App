import type {
    ChatRequest,
    ChatResponse,
    DocumentListResponse,
    IngestResponse,
    DeleteResponse,
} from "../types/api";

function getConfig() {
    const stored = localStorage.getItem("rag_settings");
    const parsed = stored ? JSON.parse(stored) : {};
    return {
        baseUrl: parsed.apiUrl || "",
        apiKey: parsed.apiKey || "dev-secret-change-me",
    };
}

async function request<T>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const { baseUrl, apiKey } = getConfig();
    const url = baseUrl ? `${baseUrl}${path}` : path;

    const response = await fetch(url, {
        ...options,
        headers: {
            "X-API-Key": apiKey,
            ...(options.headers ?? {}),
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail ?? "Request failed");
    }

    return response.json() as Promise<T>;
}

// ── Chat ─────────────────────────────────────────────────────────────────────

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
    return request<ChatResponse>("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
}

// ── Ingest ───────────────────────────────────────────────────────────────────

export async function ingestDocument(file: File): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append("file", file);
    return request<IngestResponse>("/api/ingest", {
        method: "POST",
        body: formData,
    });
}

// ── Documents ────────────────────────────────────────────────────────────────

export async function listDocuments(): Promise<DocumentListResponse> {
    return request<DocumentListResponse>("/api/documents");
}

export async function deleteDocument(docId: string): Promise<DeleteResponse> {
    return request<DeleteResponse>(`/api/documents/${docId}`, { method: "DELETE" });
}
