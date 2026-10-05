"use client";

import { Activity, Beaker, BookOpen, ChartNoAxesCombined, CircleDot, FlaskConical, RadioTower } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import { BackendStatus } from "@/components/system/backend-status";

const navigation = [
  { href: "/simulation", label: "Simülasyon", icon: RadioTower },
  { href: "/experiments", label: "Deneyler", icon: FlaskConical },
  { href: "/comparison", label: "Karşılaştırma", icon: ChartNoAxesCombined },
  { href: "/methodology", label: "Metodoloji", icon: BookOpen },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return <div className="app-shell">
    <aside className="sidebar">
      <Link className="brand-mark" href="/simulation" aria-label="SwarmGuard ana sayfa"><div className="brand-symbol"><CircleDot size={20} strokeWidth={1.8} /></div><div><p className="text-sm font-bold tracking-[0.16em] text-white">SWARMGUARD</p><p className="mt-0.5 text-[9px] uppercase tracking-[0.2em] text-slate-600">Cyber resilience lab</p></div></Link>
      <nav className="mt-10 space-y-1" aria-label="Ana menü">{navigation.map(({ href, label, icon: Icon }) => { const active = pathname === href; return <Link className={cn("nav-item", active && "nav-item-active")} href={href} key={href}><Icon size={17} strokeWidth={1.8} /><span>{label}</span>{active && <span className="ml-auto size-1.5 rounded-full bg-cyan-300" />}</Link>; })}</nav>
      <div className="mt-auto rounded-2xl border border-white/[0.06] bg-white/[0.025] p-4"><div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500"><Beaker size={13} /> Araştırma sürümü</div><p className="mt-3 text-xs leading-5 text-slate-600">%95 GA, veri dışa aktarma ve deney manifestleri aktif.</p></div>
    </aside>
    <div className="workspace"><header className="topbar"><div className="flex items-center gap-2.5"><Activity className="text-cyan-300" size={15} /><span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">Sistem gözlem katmanı</span></div><BackendStatus /></header><div className="page-canvas">{children}</div></div>
    <nav className="mobile-nav" aria-label="Mobil menü">{navigation.map(({ href, label, icon: Icon }) => <Link className={cn("mobile-nav-item", pathname === href && "text-cyan-200")} href={href} key={href}><Icon size={18} /><span>{label}</span></Link>)}</nav>
  </div>;
}
