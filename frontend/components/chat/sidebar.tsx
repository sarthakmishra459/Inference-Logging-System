"use client";

import Link from "next/link";
import { BarChart3, MessageSquarePlus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatStore } from "@/store/chat-store";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const conversations = useChatStore((state) => state.conversations);
  const activeConversationId = useChatStore((state) => state.activeConversationId);
  const selectConversation = useChatStore((state) => state.selectConversation);
  const deleteConversation = useChatStore((state) => state.deleteConversation);
  const newConversation = useChatStore((state) => state.newConversation);

  return (
    <aside className="hidden h-screen w-80 shrink-0 border-r bg-card/70 md:flex md:flex-col">
      <div className="flex items-center gap-2 border-b p-3">
        <Button className="flex-1 justify-start" variant="secondary" onClick={newConversation}>
          <MessageSquarePlus size={17} />
          New chat
        </Button>
        <Button asChild variant="ghost" size="icon" aria-label="Analytics">
          <Link href="/analytics">
            <BarChart3 size={18} />
          </Link>
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="space-y-1 p-3">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={cn(
                "group flex items-center gap-2 rounded-md px-2 py-2 text-sm hover:bg-secondary",
                activeConversationId === conversation.id && "bg-secondary"
              )}
            >
              <button
                className="min-w-0 flex-1 text-left"
                onClick={() => void selectConversation(conversation.id)}
              >
                <div className="truncate font-medium">{conversation.title}</div>
                <div className="truncate text-xs text-muted-foreground">
                  {conversation.last_message_preview ?? "No messages yet"}
                </div>
              </button>
              <button
                className="rounded p-1 text-muted-foreground opacity-0 hover:bg-destructive hover:text-white group-hover:opacity-100"
                onClick={() => void deleteConversation(conversation.id)}
                aria-label="Delete conversation"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
