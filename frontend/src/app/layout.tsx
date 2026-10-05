import type { Metadata } from "next";

import { AppShell } from "@/components/layout/app-shell";

import "@xyflow/react/dist/style.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "SwarmGuard",
  description: "UAV cyber-resilience research laboratory",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr">
      <body><AppShell>{children}</AppShell></body>
    </html>
  );
}
