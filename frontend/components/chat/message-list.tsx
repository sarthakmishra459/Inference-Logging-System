"use client";

import { useEffect, useRef } from "react";
import { Bot, User } from "lucide-react";

import { MarkdownMessage } from "@/components/chat/markdown-message";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatStore } from "@/store/chat-store";
import { cn } from "@/lib/utils";

export function MessageList() {
  const messages = useChatStore((state) => state.messages);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex min-h-0 flex-1 items-center justify-center px-6 text-center">
        <div className="max-w-xl">
          <h1 className="text-3xl font-semibold tracking-normal">Inference Logging System</h1>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            Start a conversation to stream a Gemini response while the backend captures latency,
            token usage, status, previews, and conversation metadata.
          </p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="min-h-0 flex-1">
      <div className="mx-auto flex w-full md:max-w-full max-w-3xl flex-col gap-6 px-4 py-8">
        {messages.map((message, index) => {
          const isUser = message.role === "user";
          const isLastStreaming = isStreaming && index === messages.length - 1 && !message.content;
          return (
            <div key={message.id} className={cn("flex gap-3", isUser && "justify-end")}>
              {!isUser && (
                <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/15 text-primary">
                  <Bot size={18} />
                </div>
              )}
              <div
                className={cn(
                  "min-w-0 max-w-[84%] rounded-lg px-4 py-3 text-sm leading-6",
                  isUser ? "bg-primary text-primary-foreground" : "bg-secondary/70 text-foreground"
                )}
              >
                {isLastStreaming ? (
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-primary" />
                    Thinking
                  </div>
                ) : isUser ? (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <MarkdownMessage content={message.content} />
                )}
              </div>
              {isUser && (
                <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-secondary text-foreground">
                  <User size={18} />
                </div>
              )}
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
