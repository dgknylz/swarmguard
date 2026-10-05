"use client";

import { useEffect, useState } from "react";

import { apiClient } from "@/lib/api/client";

type BackendState = "checking" | "online" | "offline";

export function BackendStatus() {
  const [state, setState] = useState<BackendState>("checking");

  useEffect(() => {
    const controller = new AbortController();
    apiClient.health().then(() => setState("online")).catch(() => setState("offline"));
    return () => controller.abort();
  }, []);

  const label = state === "checking" ? "Kontrol ediliyor" : state === "online" ? "API çevrimiçi" : "API çevrimdışı";
  return <div className="flex items-center gap-2 rounded-full border border-white/[0.07] bg-white/[0.035] px-3 py-1.5"><span className={`status-dot ${state === "online" ? "status-dot-online" : "status-dot-idle"}`} /><span className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">{label}</span></div>;
}
