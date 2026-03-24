import { useEffect, useRef, useState } from "react";
import type { PracticeInfo, ChatMessage } from "../types";
import { CONFIG_AREAS } from "../types";
import { sendChat } from "../api";
import ConfigSidebar from "./ConfigSidebar";
import ScheduleCallLink from "./ScheduleCallLink";

const PHASE_ORDER = CONFIG_AREAS.map((a) => a.key);

function phaseIndex(phase: string) {
  const idx = PHASE_ORDER.indexOf(phase);
  return idx === -1 ? PHASE_ORDER.length : idx;
}

interface Props {
  practice: PracticeInfo;
  onComplete: (summaryText: string) => void;
}

interface DisplayMessage {
  role: "user" | "assistant";
  content: string;
}

const INIT_PROMPT =
  "The practice has confirmed their details. Begin the configuration conversation. Acknowledge their practice and ask the first configuration question.";

function isComplete(text: string) {
  return text.toUpperCase().includes("CONFIGURATION COMPLETE");
}

function formatContent(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

function truncate(s: string, max: number) {
  return s.length > max ? s.slice(0, max).trimEnd() + "…" : s;
}

export default function Chat({ practice, onComplete }: Props) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activePhase, setActivePhase] = useState("patient_demographics");
  const [completedPhases, setCompletedPhases] = useState<Map<string, string>>(new Map());
  const [escalation, setEscalation] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const initialized = useRef(false);
  const prevPhase = useRef("patient_demographics");
  const lastUserMsg = useRef("");
  const sessionId = useRef(crypto.randomUUID());

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    callAI(INIT_PROMPT, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 168)}px`;
  }, [input]);

  async function callAI(userText: string, showUserBubble: boolean) {
    setLoading(true);
    setEscalation(false);
    const newHistory: ChatMessage[] = [
      ...history,
      { role: "user", content: userText },
    ];
    setHistory(newHistory);

    if (showUserBubble) {
      lastUserMsg.current = userText;
      setMessages((prev) => [...prev, { role: "user", content: userText }]);
    }

    try {
      const data = await sendChat(newHistory, practice, sessionId.current);
      setHistory((prev) => [...prev, { role: "assistant", content: data.response }]);
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);

      const previousPhase = prevPhase.current;

      const advanced =
        data.current_phase !== previousPhase &&
        phaseIndex(data.current_phase) > phaseIndex(previousPhase) &&
        lastUserMsg.current;

      if (advanced) {
        const pi = phaseIndex(previousPhase);
        const ni = phaseIndex(data.current_phase);
        const primaryLabel =
          data.sidebar_caption?.trim() &&
          data.validation_quality !== "nonsense"
            ? truncate(data.sidebar_caption.trim(), 60)
            : truncate(lastUserMsg.current, 60);
        setCompletedPhases((prev) => {
          const next = new Map(prev);
          for (let i = pi; i < ni && i < PHASE_ORDER.length; i++) {
            const k = PHASE_ORDER[i];
            if (!next.has(k)) {
              next.set(k, i === pi ? primaryLabel : "—");
            }
          }
          return next;
        });
      }

      if (data.needs_escalation) {
        setEscalation(true);
      }

      if (isComplete(data.response)) {
        setCompletedPhases((prev) => {
          const next = new Map(prev);
          if (lastUserMsg.current && PHASE_ORDER.includes(previousPhase)) {
            const cap =
              data.sidebar_caption?.trim() &&
              data.validation_quality !== "nonsense"
                ? truncate(data.sidebar_caption.trim(), 60)
                : truncate(lastUserMsg.current, 60);
            next.set(previousPhase, cap);
          }
          for (const { key } of CONFIG_AREAS) {
            if (!next.has(key)) {
              next.set(key, "Completed");
            }
          }
          return next;
        });
        setTimeout(() => onComplete(data.response), 1400);
      }

      prevPhase.current = data.current_phase;
      setActivePhase(data.current_phase);
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : "Connection error.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ ${errMsg}` },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleSend() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    callAI(text, true);
  }

  function handleRevise(phaseKey: string, phaseLabel: string) {
    if (loading) return;
    setCompletedPhases((prev) => {
      const next = new Map(prev);
      next.delete(phaseKey);
      return next;
    });
    setActivePhase(phaseKey);
    prevPhase.current = phaseKey;
    const reviseMsg = `I'd like to change my ${phaseLabel} settings.`;
    callAI(reviseMsg, true);
  }

  return (
    <div className="chat-layout">
      <div className="card chat-card">
        <h2>Configure Your Account</h2>
        <p className="sub">
          Answer a few questions and I'll set everything up for your practice.
        </p>

        <div className="chat-area" ref={chatRef}>
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role === "user" ? "user" : "ai"}`}>
              <div>
                <div className="label">
                  {m.role === "user" ? "You" : "AI Assistant"}
                </div>
                <div
                  className="bubble"
                  dangerouslySetInnerHTML={{ __html: formatContent(m.content) }}
                />
              </div>
            </div>
          ))}
          {loading && (
            <div className="msg ai">
              <div>
                <div className="label">AI Assistant</div>
                <div className="bubble">
                  <div className="typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {escalation && (
          <div className="escalation-banner">
            <div className="escalation-icon">🔍</div>
            <div className="escalation-body">
              <strong>Specialist recommended</strong>
              <span>Part of this setup needs hands-on configuration. A PrescriberPoint specialist will follow up.</span>
            </div>
            <ScheduleCallLink
              label="Call +17743579384"
              dialPhone="+17743579384"
              variant="sm"
            />
          </div>
        )}

        <div className="input-row chat-input-row">
          <textarea
            ref={inputRef}
            className="chat-input"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Type your response… (Shift+Enter for a new line)"
            disabled={loading}
            aria-label="Message"
          />
          <button
            className="btn btn-primary"
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>

      <ConfigSidebar
        activePhase={activePhase}
        completedPhases={completedPhases}
        loading={loading}
        onRevise={handleRevise}
      />
    </div>
  );
}
