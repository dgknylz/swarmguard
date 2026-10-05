import { Badge } from "@/components/ui/badge";

type PageHeaderProps = { eyebrow: string; title: string; description: string; badge?: string; actions?: React.ReactNode };

export function PageHeader({ eyebrow, title, description, badge, actions }: PageHeaderProps) {
  return <div className="page-header"><div><div className="mb-3 flex items-center gap-3"><p className="eyebrow">{eyebrow}</p>{badge && <Badge tone="info">{badge}</Badge>}</div><h1 className="page-title">{title}</h1><p className="page-description">{description}</p></div>{actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}</div>;
}
