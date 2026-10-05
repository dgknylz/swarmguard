import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

type MetricCardProps = { label: string; value: string; detail: string; icon: LucideIcon; tone?: "cyan" | "emerald" | "rose" | "amber" };

const tones = {
  cyan: "bg-cyan-300/10 text-cyan-200 ring-cyan-300/15",
  emerald: "bg-emerald-300/10 text-emerald-200 ring-emerald-300/15",
  rose: "bg-rose-300/10 text-rose-200 ring-rose-300/15",
  amber: "bg-amber-300/10 text-amber-200 ring-amber-300/15",
};

export function MetricCard({ label, value, detail, icon: Icon, tone = "cyan" }: MetricCardProps) {
  return <div className="metric-card"><div className={cn("flex size-9 items-center justify-center rounded-xl ring-1", tones[tone])}><Icon size={16} strokeWidth={1.8} /></div><div className="min-w-0"><p className="metric-label">{label}</p><p className="mt-1 text-xl font-semibold tracking-[-0.04em] text-white">{value}</p><p className="mt-1 truncate text-[11px] text-slate-600">{detail}</p></div></div>;
}
