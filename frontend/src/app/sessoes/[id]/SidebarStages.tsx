import { ReactNode } from "react";

interface SidebarEtapaProps {
  etapaAtual: number;
  totalEtapas: number;
  nomeEtapa: string;
  titulo: string;
  children: ReactNode;
}

export function SidebarStages({ 
  etapaAtual, 
  totalEtapas, 
  nomeEtapa, 
  titulo, 
  children 
}: SidebarEtapaProps) {
  return (
    <aside className="w-full bg-surface border border-line rounded-xl p-6 flex flex-col gap-6 sticky top-8 shadow-sm">
      <div className="flex flex-col gap-1.5">
        <span className="font-mono text-[12px] font-medium text-fg-muted uppercase tracking-[0.04em]">
          Etapa {etapaAtual} de {totalEtapas} · {nomeEtapa}
        </span>
        <h2 className="text-[18px] font-semibold text-fg">
          {titulo}
        </h2>
      </div>
      
      {children}
    </aside>
  );
}