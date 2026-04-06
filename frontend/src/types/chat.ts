// Types for chat message state in the UI

export interface Message {
    id: string;
    role: "user" | "ai";
    content: string;
    sources?: Array<{ filename: string; snippet: string }>;
    timestamp: Date;
}
