import { Binary, Braces, Network, Shield } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

const sections = [
  { icon: Network, index: "01", title: "Dinamik ağ modeli", text: "İHA konumları, Öklid mesafesi ve haberleşme menzili üzerinden zamanla değişen G(t) grafı." },
  { icon: Binary, index: "02", title: "SIS yayılımı", text: "Senkron güncelleme ve P(S→I) = 1 − (1 − β)ᵏ enfeksiyon olasılığı." },
  { icon: Shield, index: "03", title: "Savunma ailesi", text: "Savunmasız, rastgele, merkeziyet tabanlı ve GTAD yöntemlerinin ortak deney sözleşmesi." },
  { icon: Braces, index: "04", title: "Tekrarlanabilirlik", text: "Seed tabanlı senaryolar, eşleştirilmiş deney tasarımı ve açık metrik tanımları." },
];

export default function MethodologyPage() {
  return <main><PageHeader eyebrow="Bilimsel yöntem" title="Her kararın arkasında açık bir model." description="Simülasyon varsayımları, algoritma sözleşmeleri ve deney tasarımı tek bir doğrulanabilir metodoloji altında tutulur." badge="Sürüm 1.0" /><section className="grid gap-4 md:grid-cols-2">{sections.map(({ icon: Icon, index, title, text }) => <Card className="group p-6 transition-colors hover:border-cyan-300/15" key={index}><div className="flex items-start justify-between"><div className="flex size-10 items-center justify-center rounded-xl bg-white/[0.04] text-slate-400 ring-1 ring-white/[0.06]"><Icon size={17} /></div><span className="font-mono text-[10px] text-slate-700">{index}</span></div><CardTitle className="mt-8 text-base">{title}</CardTitle><CardDescription className="mt-3 max-w-xl">{text}</CardDescription></Card>)}</section><Card className="mt-4 p-6"><div className="flex items-center justify-between"><div><CardTitle>Doğrulama durumu</CardTitle><CardDescription className="mt-1">Backend, API ve arayüz kontrolleri</CardDescription></div><Badge tone="healthy">111 test geçti</Badge></div></Card></main>;
}
