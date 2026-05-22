export type Conversation = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview?: string | null;
};

export type Message = {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
};

export type DashboardMetrics = {
  average_latency_ms: number;
  total_requests: number;
  total_tokens: number;
  error_rate: number;
  requests_over_time: { timestamp: string; requests: number; errors: number }[];
  provider_usage: { name: string; value: number }[];
  model_usage: { name: string; value: number }[];
};
