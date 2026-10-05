"use client";

import { Activity, CirclePause, FlaskConical, Gauge, MonitorPlay, Network, Play, RotateCcw, ShieldAlert, Sparkles, Square, Waypoints } from "lucide-react";
import { useCallback, useState } from "react";

import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { useSimulationController } from "@/hooks/use-simulation-controller";
import { useSimulationStore } from "@/stores/simulation-store";

import { EventLog } from "./event-log";
import { LiveMetricsChart } from "./live-metrics-chart";
import { ReplayControls } from "./replay-controls";
import { defaultSimulationConfig, demoSimulationConfig, ScenarioForm } from "./scenario-form";
import { SwarmGraph, type DisplayMode } from "./swarm-graph";

const connectionLabels = {
  disconnected: "Bağlı değil",
  connecting: "Bağlanıyor",
  connected: "Canlı",
  reconnecting: "Yeniden bağlanıyor",
  completed: "Tamamlandı",
  failed: "Bağlantı hatası",
};

const percentage = (value: number | undefined) => value === undefined ? "—" : `%${(value * 100).toFixed(1)}`;
const decimal = (value: number | undefined) => value === undefined ? "—" : value.toFixed(3);

export function SimulationWorkspace() {
  const [config, setConfig] = useState(defaultSimulationConfig);
  const [replayIndex, setReplayIndex] = useState<number | null>(null);
  const [focusedNodeId, setFocusedNodeId] = useState<number | null>(null);
  const [displayMode, setDisplayMode] = useState<DisplayMode>("scientific");
  const controller = useSimulationController();
  const frames = useSimulationStore((state) => state.frames);
  const latestFrame = useSimulationStore((state) => state.latestFrame);
  const error = useSimulationStore((state) => state.error);
  const active = controller.status === "created" || controller.status === "running" || controller.status === "paused";
  const displayedFrame = replayIndex === null ? latestFrame : (frames[replayIndex] ?? latestFrame);
  const metrics = displayedFrame?.metrics;
  const selectReplayIndex = useCallback((index: number) => setReplayIndex(index), []);
  const returnToLive = useCallback(() => { setReplayIndex(null); setFocusedNodeId(null); }, []);
  const start = () => { returnToLive(); void controller.start(config); };
  const reset = () => { returnToLive(); controller.reset(); };
  const presentation = displayMode === "presentation";

  const actions = <>
    <Button onClick={() => setDisplayMode(presentation ? "scientific" : "presentation")} variant="secondary">{presentation ? <FlaskConical size={15} /> : <MonitorPlay size={15} />} {presentation ? "Bilimsel mod" : "Sunum modu"}</Button>
    {!active && <Button onClick={() => setConfig(demoSimulationConfig)} variant="secondary"><Sparkles size={15} /> Demo yükle</Button>}
    <Button disabled={!controller.session && !frames.length} onClick={reset} variant="secondary"><RotateCcw size={15} /> Sıfırla</Button>
    {controller.status === "running" && <Button disabled={controller.busy} onClick={controller.pause} variant="secondary"><CirclePause size={15} /> Duraklat</Button>}
    {controller.status === "paused" && <Button disabled={controller.busy} onClick={controller.resume}><Play fill="currentColor" size={14} /> Devam ettir</Button>}
    {active && <Button disabled={controller.busy} onClick={controller.stop} variant="danger"><Square fill="currentColor" size={12} /> Durdur</Button>}
    {!active && <Button disabled={controller.busy} onClick={start}><Play fill="currentColor" size={14} /> {controller.busy ? "Başlatılıyor" : "Simülasyonu başlat"}</Button>}
  </>;

  return <main>
    <PageHeader eyebrow={presentation ? "Sunum görünümü" : "Canlı operasyon alanı"} title={presentation ? "Sürü direncini tek bakışta anlat." : "Sürü ağını gözlemle ve müdahaleyi yönet."} description={presentation ? "Saldırı yayılımı ve adaptif topoloji müdahaleleri, dikkat dağıtmayan sahne görünümünde." : "Dinamik topoloji, saldırı yayılımı ve bağlantısallık metriklerini aynı zaman ekseninde takip et."} badge={`${displayMode === "scientific" ? "SCIENTIFIC" : "PRESENTATION"} · ${replayIndex === null ? "CANLI" : "REPLAY"} · t = ${displayedFrame?.step ?? 0}`} actions={actions} />
    {error && <div className="mb-4 rounded-xl border border-rose-300/20 bg-rose-300/10 px-4 py-3 text-xs text-rose-200" role="alert">{error}</div>}
    <section className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <MetricCard icon={ShieldAlert} label="Enfekte" value={metrics ? `${metrics.infected_count} · ${percentage(metrics.infected_ratio)}` : "—"} detail="Aktif etkilenen düğümler" tone="rose" />
      <MetricCard icon={Network} label="Bağlantı" value={percentage(metrics?.largest_component_ratio)} detail={`${metrics?.edge_count ?? 0} aktif kenar`} tone="emerald" />
      <MetricCard icon={Activity} label="λ₂" value={decimal(metrics?.algebraic_connectivity)} detail="Algebraic connectivity" />
      <MetricCard icon={Gauge} label="Efficiency" value={decimal(metrics?.global_efficiency)} detail="Global ağ verimi" tone="amber" />
    </section>
    <section className={`mt-4 grid gap-4 ${presentation ? "grid-cols-1" : "xl:grid-cols-[300px_minmax(0,1fr)_300px]"}`}>
      {!presentation && <Card className="p-5"><CardHeader><div><CardTitle>Senaryo ayarları</CardTitle><CardDescription className="mt-1">Başlangıç parametreleri</CardDescription></div><Badge tone={active ? "warning" : "neutral"}>{active ? "Kilitli" : "Hazır"}</Badge></CardHeader><div className="mt-6"><ScenarioForm disabled={active} onChange={setConfig} value={config} /></div></Card>}
      <Card className={`grid-field overflow-hidden ${presentation ? "presentation-stage min-h-[720px]" : "min-h-[560px]"}`}><div className="relative z-10 flex items-center justify-between border-b border-white/[0.055] p-5"><div><CardTitle>{presentation ? "SwarmGuard · Mission View" : "Swarm topology"}</CardTitle><CardDescription className="mt-1">{presentation ? "Kırmızı: enfekte · Camgöbeği: yeni bağlantı · Kesikli: kesilen hat" : "Canlı ve geçmiş ağ görünümü"}</CardDescription></div><Badge tone={replayIndex !== null ? "info" : controller.connection === "connected" ? "healthy" : controller.connection === "failed" ? "infected" : "neutral"}>{replayIndex !== null ? "Replay" : <><span className={`status-dot ${controller.connection === "connected" ? "status-dot-online" : "status-dot-idle"}`} /> {connectionLabels[controller.connection]}</>}</Badge></div><div className={presentation ? "h-[605px]" : "h-[445px]"}><SwarmGraph displayMode={displayMode} focusedNodeId={focusedNodeId} frame={displayedFrame} /></div><ReplayControls frames={frames} index={replayIndex} onIndexChange={selectReplayIndex} onLive={returnToLive} /></Card>
      {!presentation && <Card className="p-5"><CardHeader><div><CardTitle>Olay akışı</CardTitle><CardDescription className="mt-1">Filtrele, dışa aktar veya olaya git</CardDescription></div><Waypoints className="text-slate-600" size={17} /></CardHeader><div className="mt-6"><EventLog frames={frames} onSelectEvent={(event) => { const index = frames.findIndex((frame) => frame.step === event.step); if (index >= 0) setReplayIndex(index); setFocusedNodeId(event.node_id); }} /></div></Card>}
    </section>
    {!presentation && <section className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_300px]">
      <Card className="p-5"><CardHeader><div><CardTitle>Canlı sistem metrikleri</CardTitle><CardDescription className="mt-1">Enfeksiyon, bağlantısallık ve verim zaman serileri</CardDescription></div><Badge tone={frames.length ? "info" : "neutral"}>{frames.length} kare</Badge></CardHeader><div className="mt-3"><LiveMetricsChart frames={frames} /></div></Card>
      <Card className="p-5"><CardHeader><div><CardTitle>Oturum özeti</CardTitle><CardDescription className="mt-1">Geçerli çalışma durumu</CardDescription></div></CardHeader><div className="mt-6 space-y-4">{[["Oturum", controller.session?.id.slice(0, 8) ?? "—"], ["Durum", controller.status], ["Görünüm", replayIndex === null ? "canlı" : "replay"], ["Savunma", displayedFrame?.defense_report?.algorithm ?? config.defense_strategy], ["Aday", String(displayedFrame?.defense_report?.metadata.candidate_count ?? 0)], ["Seçilen", String(displayedFrame?.defense_report?.metadata.selected_candidate_count ?? 0)], ["Müdahale", String(displayedFrame?.defense_report?.applied_actions.length ?? 0)], ["Maliyet", String(displayedFrame?.defense_report?.intervention_cost ?? 0)], ["Maks. risk", displayedFrame?.defense_report?.metadata.max_risk?.toFixed(3) ?? "—"], ["Kare", String(frames.length)], ["Seed", String(config.seed)]].map(([label, value]) => <div className="flex items-center justify-between border-b border-white/[0.055] pb-3" key={label}><span className="text-xs text-slate-600">{label}</span><span className="max-w-36 truncate font-mono text-[11px] text-slate-300">{value}</span></div>)}</div></Card>
    </section>}
  </main>;
}
