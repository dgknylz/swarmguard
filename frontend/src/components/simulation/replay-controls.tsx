"use client";

import { ChevronLeft, ChevronRight, Pause, Play, Radio } from "lucide-react";
import { useEffect, useState } from "react";

import type { SimulationFrame } from "@/lib/api/schemas";

export function ReplayControls({ frames, index, onIndexChange, onLive }: { frames: SimulationFrame[]; index: number | null; onIndexChange: (index: number) => void; onLive: () => void; }) {
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const current = index ?? Math.max(0, frames.length - 1);

  useEffect(() => {
    if (!playing || !frames.length) return;
    const timer = window.setInterval(() => {
      const active = index ?? frames.length - 1;
      if (active >= frames.length - 1) { setPlaying(false); return; }
      onIndexChange(active + 1);
    }, 600 / speed);
    return () => window.clearInterval(timer);
  }, [frames.length, index, onIndexChange, playing, speed]);

  if (!frames.length) return null;

  return <div className="border-t border-white/[0.055] bg-black/15 px-4 py-3" aria-label="Replay kontrolleri"><div className="flex flex-wrap items-center gap-3">
    <button aria-label="Önceki kare" className="rounded-lg border border-white/10 p-2 text-slate-400 hover:text-white" disabled={current === 0} onClick={() => onIndexChange(Math.max(0, current - 1))} type="button"><ChevronLeft size={14} /></button>
    <button aria-label={playing ? "Replay duraklat" : "Replay oynat"} className="rounded-lg bg-cyan-300 p-2 text-slate-950" onClick={() => { if (index === null || current === frames.length - 1) onIndexChange(0); setPlaying((value) => !value); }} type="button">{playing ? <Pause size={14} fill="currentColor" /> : <Play size={14} fill="currentColor" />}</button>
    <button aria-label="Sonraki kare" className="rounded-lg border border-white/10 p-2 text-slate-400 hover:text-white" disabled={current === frames.length - 1} onClick={() => onIndexChange(Math.min(frames.length - 1, current + 1))} type="button"><ChevronRight size={14} /></button>
    <input aria-label="Replay zaman çizelgesi" className="min-w-32 flex-1 accent-cyan-300" max={frames.length - 1} min={0} onChange={(event) => onIndexChange(Number(event.target.value))} type="range" value={current} />
    <span className="min-w-16 font-mono text-[10px] text-slate-500">t = {frames[current]?.step ?? 0}</span>
    <select aria-label="Replay hızı" className="form-input !w-auto !py-1.5 text-[10px]" onChange={(event) => setSpeed(Number(event.target.value))} value={speed}><option value={0.5}>0.5×</option><option value={1}>1×</option><option value={2}>2×</option><option value={4}>4×</option></select>
    <button className="flex items-center gap-1 rounded-lg border border-cyan-300/20 px-2.5 py-2 text-[10px] text-cyan-200" onClick={() => { setPlaying(false); onLive(); }} type="button"><Radio size={11} /> Canlıya dön</button>
  </div></div>;
}
