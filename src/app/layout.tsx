import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "CompasScan - Competitive Intelligence Tool",
  description: "Automated competitive intelligence tool powered by AI to analyze brand competitors",
  keywords: ["competitive intelligence", "competitor analysis", "brand research", "AI-powered analysis"],
  authors: [{ name: "CompasScan Team" }],
  openGraph: {
    title: "CompasScan - Competitive Intelligence Tool",
    description: "Automated competitive intelligence tool powered by AI",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="antialiased min-h-screen flex flex-col">{children}</body>
    </html>
  );
}
