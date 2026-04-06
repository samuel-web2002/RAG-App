import { useState, useRef, useEffect, useCallback } from "react";
import type { Message } from "../types/chat";
import { sendChat } from "../api/client";

const SUGGESTIONS = [
    "Summarize the document",
    "What are the key points?",
    "Explain the main topic",
    "List the important facts",
];

interface Props {
    sessionId: string;
}

export function ChatWindow({ sessionId }: Props) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const bottomRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    const adjustTextarea = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
        }
    };

    const sendMessage = useCallback(
        async (text: string) => {
            if (!text.trim() || loading) return;
            setError(null);

            const userMsg: Message = {
                id: crypto.randomUUID(),
                role: "user",
                content: text.trim(),
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, userMsg]);
            setInput("");
            if (textareaRef.current) textareaRef.current.style.height = "auto";
            setLoading(true);

            try {
                const res = await sendChat({ message: text.trim(), session_id: sessionId });

                const sources = res.sources.map((s) => ({
                    filename: String(s.metadata?.source_filename ?? "source"),
                    snippet: s.content.slice(0, 120) + "…",
                }));

                const aiMsg: Message = {
                    id: crypto.randomUUID(),
                    role: "ai",
                    content: res.answer,
                    sources,
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, aiMsg]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Something went wrong.");
            } finally {
                setLoading(false);
            }
        },
        [loading, sessionId]
    );

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input);
        }
    };

    return (
        <div className="chat-view">
            {/* Header */}
            <div className="chat-header">
                <span className="chat-header-title">Chat</span>
                <span className="chat-header-badge">RAG · GPT-4o</span>
            </div>

            {/* Messages */}
            <div className="chat-messages">
                {messages.length === 0 && !loading && (
                    <div className="chat-empty-state">
                        <div className="chat-empty-icon">✦</div>
                        <p className="chat-empty-title">Ask anything about your docs</p>
                        <p className="chat-empty-subtitle">
                            Upload documents in the Documents tab, then ask questions here to get
                            AI-powered answers grounded in your content.
                        </p>
                        <div className="chat-suggestions">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    className="chat-suggestion-chip"
                                    onClick={() => sendMessage(s)}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg) => (
                    <div key={msg.id} className={`message-row ${msg.role}`}>
                        <div className={`message-avatar ${msg.role}`}>
                            {msg.role === "ai" ? "✦" : "U"}
                        </div>
                        <div className={`message-bubble ${msg.role}`}>
                            {msg.content}
                            {msg.role === "ai" && msg.sources && msg.sources.length > 0 && (
                                <div className="message-sources">
                                    <div className="message-sources-title">Sources</div>
                                    {msg.sources.map((src, i) => (
                                        <span key={i} className="message-source-chip">
                                            📄 {src.filename}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message-row ai">
                        <div className="message-avatar ai">✦</div>
                        <div className="message-bubble ai">
                            <div className="typing-indicator">
                                <div className="typing-dot" />
                                <div className="typing-dot" />
                                <div className="typing-dot" />
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="toast error">⚠ {error}</div>
                )}

                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="chat-input-area">
                <div className="chat-input-wrapper">
                    <textarea
                        ref={textareaRef}
                        className="chat-textarea"
                        placeholder="Ask a question about your documents…"
                        value={input}
                        rows={1}
                        onChange={(e) => { setInput(e.target.value); adjustTextarea(); }}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                        id="chat-input"
                    />
                    <button
                        className="chat-send-btn"
                        onClick={() => sendMessage(input)}
                        disabled={loading || !input.trim()}
                        aria-label="Send message"
                        id="send-btn"
                    >
                        ➤
                    </button>
                </div>
                <p className="chat-input-hint">Enter to send · Shift+Enter for new line</p>
            </div>
        </div>
    );
}
