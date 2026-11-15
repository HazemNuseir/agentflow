import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DME AgentFlow — Intelligent Business Automation",
  description: "Sovereign on-premise business automation platform powered by Google Gemma 4. Developed by Digital Mind Engineering (DME), Jordan.",
};

export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full flex flex-col bg-slate-900 text-slate-100 font-sans">
        {children}
      </body>
    </html>
  );
}

