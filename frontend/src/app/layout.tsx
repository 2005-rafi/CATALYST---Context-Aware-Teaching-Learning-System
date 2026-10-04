import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "@/styles/theme/theme.css";
import "./globals.css";
import UnifiedSidebar from "@/components/layout/UnifiedSidebar";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import { WorkspaceSessionProvider } from "@/components/providers/WorkspaceSessionProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RAG Document Intelligence",
  description: "Context-Aware Conversational RAG Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground h-screen flex overflow-hidden`}
      >
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <WorkspaceSessionProvider>
            <UnifiedSidebar />
            <main className="flex-1 h-screen overflow-hidden min-w-0 relative flex flex-col">
              {children}
            </main>
          </WorkspaceSessionProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
