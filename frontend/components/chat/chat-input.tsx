"use client";

import { FormEvent, KeyboardEvent, useState } from "react";
import { Send, Square } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useChatStore } from "@/store/chat-store";

export function ChatInput() {
  const [value, setValue] = useState("");
  const sendMessage = useChatStore((state) => state.sendMessage);
  const cancelStream = useChatStore((state) => state.cancelStream);
  const isStreaming = useChatStore((state) => state.isStreaming);

  const submit = async (event?: FormEvent) => {
    event?.preventDefault();
    const content = value.trim();
    if (!content || isStreaming) return;
    setValue("");
    await sendMessage(content);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submit();
    }
  };

  return (
    <form
      onSubmit={submit}
      className="shrink-0 border-t bg-background/95 px-3 py-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))] sm:px-4"
    >
      <div className="mx-auto flex items-end gap-2">
        <Textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask anything and watch inference metadata flow into the dashboard..."
          className="h-10 max-h-44 min-h-10 resize-none py-2"
          disabled={isStreaming}
        />
        {isStreaming ? (
          <Button type="button" size="icon" variant="destructive" onClick={cancelStream} aria-label="Cancel stream">
            <Square size={18} />
          </Button>
        ) : (
          <Button type="submit" size="icon" aria-label="Send message" disabled={!value.trim()}>
            <Send size={18} />
          </Button>
        )}
      </div>
    </form>
  );
}
