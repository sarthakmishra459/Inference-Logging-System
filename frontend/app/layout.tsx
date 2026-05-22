import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Inference Logging System",
  description: "Streaming LLM chat with inference logging and analytics."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
