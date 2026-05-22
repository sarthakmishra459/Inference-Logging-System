import type { Conversation, DashboardMetrics, Message } from "@/lib/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type MongoConversation = Omit<Conversation, "id"> & { _id?: string; id?: string };
type MongoMessage = Omit<Message, "id"> & { _id?: string; id?: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    cache: "no-store"
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  conversations: async () =>
    (await request<MongoConversation[]>("/conversations")).map((item) => ({
      ...item,
      id: item.id ?? item._id ?? ""
    })),
  messages: async (conversationId: string) =>
    (await request<MongoMessage[]>(`/conversations/${conversationId}/messages`)).map((item) => ({
      ...item,
      id: item.id ?? item._id ?? ""
    })),
  deleteConversation: (conversationId: string) =>
    fetch(`${API_BASE_URL}/conversations/${conversationId}`, { method: "DELETE" }),
  metrics: () => request<DashboardMetrics>("/metrics/dashboard")
};

export type StreamEvent =
  | { event: "conversation"; data: { conversation_id: string; title: string } }
  | { event: "token"; data: { text: string } }
  | { event: "error"; data: { message: string } }
  | { event: "done"; data: { conversation_id: string } };

export async function* streamChat(
  body: { message: string; conversation_id?: string | null; model?: string | null },
  signal: AbortSignal
): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal
  });
  if (!response.ok || !response.body) {
    throw new Error(await response.text());
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const lines = frame.split("\n");
      const event = lines.find((line) => line.startsWith("event:"))?.replace("event:", "").trim();
      const data = lines.find((line) => line.startsWith("data:"))?.replace("data:", "").trim();
      if (!event || !data) continue;
      yield { event, data: JSON.parse(data) } as StreamEvent;
    }
  }
}
