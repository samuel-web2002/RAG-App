// API types matching backend schemas

export interface ChatRequest {
    message: string;
    session_id?: string;
}

export interface SourceDocument {
    content: string;
    metadata: Record<string, unknown>;
}

export interface ChatResponse {
    answer: string;
    session_id: string;
    sources: SourceDocument[];
}

export interface IngestResponse {
    status: "success" | "error";
    filename: string;
    chunks_created: number;
    message: string;
}

export interface DocumentInfo {
    id: string;
    filename: string;
    source: string;
    chunk_count: number;
}

export interface DocumentListResponse {
    documents: DocumentInfo[];
    total: number;
}

export interface DeleteResponse {
    status: "success" | "error";
    deleted_chunks: number;
}
