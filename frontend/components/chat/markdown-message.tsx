"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils";

export function MarkdownMessage({ content, compact = false }: { content: string; compact?: boolean }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className={cn(
        "prose prose-invert max-w-none prose-pre:rounded-md prose-pre:border prose-pre:border-border prose-pre:bg-black/40 prose-code:text-teal-200",
        compact && "prose-p:my-1"
      )}
    >
      {content || " "}
    </ReactMarkdown>
  );
}
