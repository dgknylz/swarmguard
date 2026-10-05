"use client";

import { Download, FileJson, FlaskConical, Layers3, Play, Settings2 } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/layout/page-header";
import { defaultSimulationConfig } from "@/components/simulation/scenario-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, experimentArtifactUrl } from "@/lib/api/client";
import type { ExperimentResult } from "@/lib/api/schemas";

const experimentScenario = {
  ...defaultSimulationConfig,
  node_count: 20,
  steps: 20,
  speed: 6,
  step_interval_ms: 0,
};
const seeds = [42, 43, 44];
const percentage = (value: number | undefined) => value === undefined ? "—" : `${(value * 100).toFixed(1)}%`;
const signed = (value: number | undefined) => value === undefined ? "—" : `${value >= 0 ? "+" : ""}${value.toFixed(3)}`;
const interval = (low: number | undefined, high: number | undefined) => low === undefined || high === undefined ? "—" : `[${low.toFixed(3)}, ${high.toFixed(3)}]`;
const artifactClass = "inline-flex h-9 items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.055] px-3 text-xs font-semibold text-slate-100 transition-colors hover:border-white/20 hover:bg-white/[0.09]";

export default function ExperimentsPage() {
  const [result, setResult] = useState<ExperimentResult | null>(null);
  const [busy, setBusy] = useState<"monte_carlo" | "gtad_ablation" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async (kind: "monte_carlo" | "gtad_ablation") => {
    setBusy(kind);
    setError(null);
    try {
      const request = { scenario: experimentScenario, seeds };
      setResult(kind === "monte_carlo"
        ? await apiClient.runMonteCarlo({ ...request, strategies: ["none", "random_rewiring", "centrality_quarantine", "gtad_risk"] })
        : await apiClient.runGtadAblation(request));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Deney çalıştırılamadı");
    } finally {
      setBusy(null);
    }
  };

  const cards = [
    { icon: Settings2, title: "GTAD ablation", text: "Bağlantısallık, güvenlik ve mesafe bileşenlerinin katkısını ayrı koşularla ölç." },
    { icon: FlaskConical, title: "Monte Carlo", text: "Her savunmayı çoklu seed altında tekrarlanabilir ortalamalarla değerlendir." },
    { icon: Layers3, title: "Eşleştirilmiş seed", text: "Her yöntemin sonucu aynı seed'in savunmasız baseline koşusuyla eşleştirilir." },
  ];

  return <main>
    <PageHeader eyebrow="Araştırma çalışma alanı" title="Tek koşudan istatistiksel kanıta." description="GTAD bileşenlerini ayır, savunmaları çoklu seed ile çalıştır ve her sonucu aynı başlangıç koşulundaki baseline ile eşleştir." badge="Aktif" actions={<><Button disabled={busy !== null} onClick={() => void run("gtad_ablation")} variant="secondary"><Settings2 size={14} /> {busy === "gtad_ablation" ? "Çalışıyor" : "Ablation"}</Button><Button disabled={busy !== null} onClick={() => void run("monte_carlo")}><Play size={14} /> {busy === "monte_carlo" ? "Çalışıyor" : "Monte Carlo"}</Button></>} />
    {error && <div className="mb-4 rounded-xl border border-rose-300/20 bg-rose-300/10 px-4 py-3 text-xs text-rose-200" role="alert">{error}</div>}
    <section className="grid gap-4 lg:grid-cols-3">{cards.map(({ icon: Icon, title, text }) => <Card className="p-6" key={title}><div className="flex size-10 items-center justify-center rounded-xl bg-cyan-300/10 text-cyan-200 ring-1 ring-cyan-300/15"><Icon size={17} /></div><CardTitle className="mt-6">{title}</CardTitle><CardDescription className="mt-2 max-w-sm">{text}</CardDescription></Card>)}</section>
    <Card className="mt-4 p-6"><CardHeader><div><CardTitle>Deney sonucu</CardTitle><CardDescription className="mt-1">{result ? `${result.kind === "monte_carlo" ? "Monte Carlo" : "GTAD ablation"} · seed ${result.seeds.join(", ")}` : "Bir deney türü seçerek sonuç üret"}</CardDescription></div><div className="flex flex-wrap items-center justify-end gap-2">{result && <><a className={artifactClass} download href={experimentArtifactUrl(result.experiment_id, "export.csv")}><Download size={13} /> CSV</a><a className={artifactClass} download href={experimentArtifactUrl(result.experiment_id, "export.parquet")}><Download size={13} /> Parquet</a><a className={artifactClass} download href={experimentArtifactUrl(result.experiment_id, "manifest.json")}><FileJson size={13} /> Manifest</a></>}<Badge tone={result ? "healthy" : "neutral"}>{result?.run_count ?? 0} koşu</Badge></div></CardHeader>
      {result ? <div className="mt-6 overflow-x-auto"><table className="w-full min-w-[780px] text-left text-xs"><thead className="text-[10px] uppercase tracking-[0.12em] text-slate-600"><tr><th className="pb-3">Yöntem</th><th className="pb-3">Koşu</th><th className="pb-3">Ort. enfeksiyon · %95 GA</th><th className="pb-3">GCC</th><th className="pb-3">Efficiency</th><th className="pb-3">Müdahale</th></tr></thead><tbody>{result.summaries.map((summary) => <tr className="border-t border-white/[0.055]" key={summary.method}><td className="py-4 font-mono text-cyan-200">{summary.method}</td><td>{summary.run_count}</td><td><span>{percentage(summary.metrics.mean_infected_ratio?.mean)}</span><span className="ml-2 font-mono text-[10px] text-slate-600">{interval(summary.metrics.mean_infected_ratio?.ci95_low, summary.metrics.mean_infected_ratio?.ci95_high)}</span></td><td>{percentage(summary.metrics.mean_largest_component_ratio?.mean)}</td><td>{summary.metrics.mean_global_efficiency?.mean.toFixed(3) ?? "—"}</td><td>{summary.metrics.total_intervention_cost?.mean.toFixed(1) ?? "—"}</td></tr>)}</tbody></table></div> : <div className="mt-6 flex h-40 items-center justify-center rounded-xl border border-dashed border-white/[0.08] bg-black/10 text-xs text-slate-600">Sonuç verisi bekleniyor</div>}
    </Card>
    {result?.paired_comparisons.length ? <section className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">{result.paired_comparisons.map((comparison) => <Card className="p-5" key={comparison.method}><div className="flex items-center justify-between"><CardTitle>{comparison.method}</CardTitle><Badge tone="info">{comparison.pair_count} eş</Badge></div><CardDescription className="mt-2">Baseline: {comparison.baseline}</CardDescription><div className="mt-5 space-y-3"><div className="flex justify-between text-xs"><span className="text-slate-600">Enfeksiyon Δ</span><span className="text-right font-mono text-slate-300">{signed(comparison.mean_deltas.mean_infected_ratio)}<small className="block text-[9px] text-slate-600">{interval(comparison.delta_statistics.mean_infected_ratio?.ci95_low, comparison.delta_statistics.mean_infected_ratio?.ci95_high)}</small></span></div><div className="flex justify-between text-xs"><span className="text-slate-600">Efficiency Δ</span><span className="font-mono text-slate-300">{signed(comparison.mean_deltas.mean_global_efficiency)}</span></div><div className="flex justify-between text-xs"><span className="text-slate-600">Müdahale Δ</span><span className="font-mono text-slate-300">{signed(comparison.mean_deltas.total_intervention_cost)}</span></div></div></Card>)}</section> : null}
  </main>;
}
