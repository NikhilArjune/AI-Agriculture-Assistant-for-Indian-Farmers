"use client";

import { useState, useRef, useEffect } from "react";
import { chatApi, getApiErrorMessage } from "@/lib/api";
import toast from "react-hot-toast";
import { v4 as uuidv4 } from "uuid";

interface Message {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  confidence?: number;
  sources?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => uuidv4());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await chatApi.send({ query: text, session_id: sessionId });
      const data = res.data;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          agent: data.agent_used,
          confidence: data.confidence,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to get response. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      <div className="bg-white border-b px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">💬</span>
        <div>
          <h1 className="font-bold text-slate-800">AI Agriculture Chat</h1>
          <p className="text-xs text-slate-400">Ask anything about farming</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 mt-20">
            <div className="text-5xl mb-4">🌾</div>
            <p className="text-lg">Ask me about crops, diseases, weather, market prices, or government schemes.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-2xl rounded-2xl px-5 py-4 text-sm ${
                msg.role === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-white border border-slate-100 text-slate-800 shadow-sm"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.role === "assistant" && msg.agent && (
                <p className="text-xs text-slate-400 mt-2">
                  Agent: {msg.agent} · Confidence: {((msg.confidence || 0) * 100).toFixed(0)}%
                </p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-100 rounded-2xl px-5 py-4 shadow-sm">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="bg-white border-t px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="Ask about farming... (e.g., 'मेरे गेहूं में कीड़े लग रहे हैं')"
            className="flex-1 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-primary-600 text-white px-5 py-3 rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
