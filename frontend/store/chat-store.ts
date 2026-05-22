"use client";

import { create } from "zustand";

import { api, streamChat } from "@/lib/api";
import type { ChatState, Conversation, Message } from "@/lib/types";



const now = () => new Date().toISOString();

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  messages: [],
  activeConversationId: null,
  isStreaming: false,
  error: null,
  abortController: null,

  loadConversations: async () => {
    const conversations = await api.conversations();
    set({ conversations });
  },

  selectConversation: async (id: string) => {
    const messages = await api.messages(id);
    set({ activeConversationId: id, messages, error: null });
  },

  newConversation: () => {
    get().cancelStream();
    set({ activeConversationId: null, messages: [], error: null });
  },

  deleteConversation: async (id: string) => {
    await api.deleteConversation(id);
    const isActive = get().activeConversationId === id;
    set((state) => ({
      conversations: state.conversations.filter((item) => item.id !== id),
      activeConversationId: isActive ? null : state.activeConversationId,
      messages: isActive ? [] : state.messages
    }));
  },

  sendMessage: async (content: string) => {
    const controller = new AbortController();
    const tempUserId = crypto.randomUUID();
    const tempAssistantId = crypto.randomUUID();
    const conversationId = get().activeConversationId;

    set((state) => ({
      isStreaming: true,
      error: null,
      abortController: controller,
      messages: [
        ...state.messages,
        {
          id: tempUserId,
          conversation_id: conversationId ?? "pending",
          role: "user",
          content,
          created_at: now()
        },
        {
          id: tempAssistantId,
          conversation_id: conversationId ?? "pending",
          role: "assistant",
          content: "",
          created_at: now()
        }
      ]
    }));

    try {
      for await (const item of streamChat(
        { message: content, conversation_id: conversationId },
        controller.signal
      )) {
        if (item.event === "conversation") {
          const newConversation: Conversation = {
            id: item.data.conversation_id,
            title: item.data.title,
            created_at: now(),
            updated_at: now(),
            message_count: 0,
            last_message_preview: content
          };
          set((state) => ({
            activeConversationId: item.data.conversation_id,
            conversations: [newConversation, ...state.conversations]
          }));
        }
        if (item.event === "token") {
          set((state) => ({
            messages: state.messages.map((message) =>
              message.id === tempAssistantId
                ? { ...message, content: message.content + item.data.text }
                : message
            )
          }));
        }
        if (item.event === "error") {
          set({ error: item.data.message });
        }
      }
      await get().loadConversations();
    } catch (error) {
      if (!controller.signal.aborted) {
        set({ error: error instanceof Error ? error.message : "Streaming request failed" });
      }
    } finally {
      set({ isStreaming: false, abortController: null });
    }
  },

  cancelStream: () => {
    get().abortController?.abort();
    set({ isStreaming: false, abortController: null });
  }
}));
