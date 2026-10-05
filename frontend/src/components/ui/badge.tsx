import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type Tone = "neutral" | "healthy" | "infected" | "warning" | "info";

const toneClasses: Record<Tone, string> = {
  neutral: "border-white/10 bg-white/[0.05] text-slate-400",
  healthy: "border-emerald-300/20 bg-emerald-300/10 text-emerald-200",
  infected: "border-rose-300/20 bg-rose-300/10 text-rose-200",
  warning: "border-amber-300/20 bg-amber-300/10 text-amber-200",
  info: "border-cyan-300/20 bg-cyan-300/10 text-cyan-200",
};

export function Badge({ className, tone = "neutral", ...props }: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return <span className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em]", toneClasses[tone], className)} {...props} />;
}
