import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "cognee-ai-dm — The Ravenhollow Chronicle",
  description:
    "AI Dungeon Master with persistent world memory. The world remembers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
