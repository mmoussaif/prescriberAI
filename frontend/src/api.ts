import type { PracticeInfo, ChatMessage, ChatApiResponse } from "./types";

export async function lookupNpi(npi: string): Promise<PracticeInfo> {
  const res = await fetch(`/api/npi/${npi}`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "NPI not found.");
  }
  return res.json();
}

export async function sendChat(
  messages: ChatMessage[],
  practiceContext: PracticeInfo,
  sessionId?: string,
): Promise<ChatApiResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages,
      practice_context: practiceContext,
      session_id: sessionId,
    }),
  });
  const data = await res.json();
  if (data.detail || data.error) {
    throw new Error(data.detail || data.error);
  }
  return data;
}
