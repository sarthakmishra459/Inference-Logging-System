"use client";

import { useEffect } from "react";
import Link from "next/link";
import { BarChart3, Menu } from "lucide-react";

import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";
import { Sidebar } from "@/components/chat/sidebar";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/store/chat-store";

export function ChatLayout() {
  const loadConversations = useChatStore((state) => state.loadConversations);
  const error = useChatStore((state) => state.error);

  useEffect(() => {
    void loadConversations();
  }, [loadConversations]);

  return (
    <main className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b px-4 md:hidden">
          <Button variant="ghost" size="icon" aria-label="Menu">
            <Menu size={18} />
          </Button>
          <span className="text-sm font-semibold">Inference Logger</span>
          <Button asChild variant="ghost" size="icon" aria-label="Analytics">
            <Link href="/analytics">
              <BarChart3 size={18} />
            </Link>
          </Button>
        </header>
        {error && (
          <div className="border-b border-destructive/40 bg-destructive/10 px-4 py-2 text-sm text-red-100">
            {error}
          </div>
        )}
        <MessageList />
        <ChatInput />
      </section>
    </main>
  );
}
