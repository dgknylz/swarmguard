"use client";

import type { SimulationCreateRequest } from "@/lib/api/schemas";

type ScenarioFormProps = {
  value: SimulationCreateRequest;
  disabled?: boolean;
  onChange: (value: SimulationCreateRequest) => void;
};

type NumberKey = {
  [Key in keyof SimulationCreateRequest]: SimulationCreateRequest[Key] extends number ? Key : never;
}[keyof SimulationCreateRequest];

const numberFields: Array<{
  key: NumberKey;
  label: string;
  min: number;
  max: number;
  step?: number;
}> = [
  { key: "node_count", label: "İHA sayısı", min: 2, max: 500 },
  { key: "communication_range", label: "Haberleşme menzili", min: 10, max: 2_000 },
  { key: "speed", label: "İHA hızı", min: 0, max: 100, step: 0.5 },
  { key: "beta", label: "Enfeksiyon β", min: 0, max: 1, step: 0.01 },
  { key: "gamma", label: "İyileşme γ", min: 0, max: 1, step: 0.01 },
  { key: "steps", label: "Zaman adımı", min: 1, max: 10_000 },
  { key: "seed", label: "Seed", min: 0, max: 4_294_967_295 },
  { key: "initial_infected_count", label: "İlk enfekte", min: 1, max: 500 },
  { key: "defense_budget", label: "Müdahale bütçesi", min: 0, max: 100 },
  { key: "defense_range_multiplier", label: "Savunma menzil çarpanı", min: 1, max: 5, step: 0.1 },
  { key: "defense_max_degree", label: "Azami düğüm derecesi", min: 1, max: 499 },
];

export const defaultSimulationConfig: SimulationCreateRequest = {
  node_count: 30,
  area_width: 1_000,
  area_height: 700,
  communication_range: 230,
  speed: 8,
  beta: 0.18,
  gamma: 0.06,
  steps: 100,
  seed: 42,
  initial_infected_count: 1,
  attack_strategy: "highest_degree",
  defense_strategy: "none",
  defense_budget: 2,
  defense_range_multiplier: 1.5,
  defense_max_degree: 8,
  step_interval_ms: 100,
};

export const demoSimulationConfig: SimulationCreateRequest = {
  ...defaultSimulationConfig,
  node_count: 24,
  communication_range: 250,
  speed: 6,
  beta: 0.16,
  gamma: 0.09,
  steps: 60,
  seed: 2025,
  initial_infected_count: 2,
  attack_strategy: "highest_betweenness",
  defense_strategy: "gtad_risk",
  defense_budget: 2,
  defense_range_multiplier: 1.6,
  defense_max_degree: 7,
  step_interval_ms: 100,
};

export function ScenarioForm({ value, disabled, onChange }: ScenarioFormProps) {
  const updateNumber = (key: NumberKey, rawValue: string) => {
    const numericValue = Number(rawValue);
    const next = { ...value, [key]: Number.isFinite(numericValue) ? numericValue : 0 };
    if (key === "node_count" && next.initial_infected_count > numericValue) {
      next.initial_infected_count = Math.max(1, numericValue);
    }
    onChange(next);
  };

  return <fieldset className="space-y-4" disabled={disabled}>
    <legend className="sr-only">Simülasyon parametreleri</legend>
    <div className="grid grid-cols-2 gap-3">
      {numberFields.map((field) => <label className="space-y-1.5" key={field.key}><span className="form-label">{field.label}</span><input className="form-input" max={field.key === "initial_infected_count" ? value.node_count : field.max} min={field.min} onChange={(event) => updateNumber(field.key, event.target.value)} step={field.step ?? 1} type="number" value={value[field.key]} /></label>)}
    </div>
    <label className="block space-y-1.5"><span className="form-label">Saldırı başlangıcı</span><select className="form-input" onChange={(event) => onChange({ ...value, attack_strategy: event.target.value as SimulationCreateRequest["attack_strategy"] })} value={value.attack_strategy}><option value="random">Rastgele düğüm</option><option value="highest_degree">En yüksek degree</option><option value="highest_betweenness">En yüksek betweenness</option></select></label>
    <label className="block space-y-1.5"><span className="form-label">Savunma algoritması</span><select className="form-input" onChange={(event) => onChange({ ...value, defense_strategy: event.target.value as SimulationCreateRequest["defense_strategy"] })} value={value.defense_strategy}><option value="none">Savunma yok · referans</option><option value="random_rewiring">Rastgele yeniden bağlantı</option><option value="centrality_quarantine">Merkeziyet karantinası</option><option value="gtad_risk">GTAD · adaptif topoloji</option></select></label>
    <label className="block space-y-1.5"><span className="form-label">Simülasyon hızı</span><select className="form-input" onChange={(event) => onChange({ ...value, step_interval_ms: Number(event.target.value) })} value={value.step_interval_ms}><option value={500}>Yavaş · 500 ms</option><option value={200}>Normal · 200 ms</option><option value={100}>Hızlı · 100 ms</option><option value={25}>Çok hızlı · 25 ms</option><option value={0}>Anında</option></select></label>
  </fieldset>;
}
