"use client";

import { Construction } from "lucide-react";
import { Etapas } from "@/components/ui/Etapas";
import { AnamneseChat, useSessao, type Etapa } from "./_anamnese/AnamneseChat";
import { CenariosTela } from "./_cenarios/CenariosTela";
import { PlanoAlimentar } from "./_plano/PlanoAlimentar";

export const NUMERO_ETAPA: Record<Etapa, number> = { anamnese: 2, plano: 3, cenarios: 4, retorno: 5 };

// le a etapa salva e abre a tela dela; carregando e erro ficam com o chat
export function EtapaSessao({ sessaoId }: { sessaoId: string }) {
  const { data: sessao } = useSessao(sessaoId);
  if (!sessao || sessao.etapa === "anamnese") return <AnamneseChat sessaoId={sessaoId} />;
  if (sessao.etapa === "cenarios") return <CenariosTela sessaoId={sessaoId} />;
  if (sessao.etapa === "plano") return <PlanoAlimentar sessaoId={sessaoId} />;

  // ponytail: retorno ainda sem tela
  const atual = NUMERO_ETAPA[sessao.etapa];
  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <Etapas atual={atual} compacta />
      <div className="px-4 py-2 md:px-8 md:py-4 border-b border-line">
        <Etapas atual={atual} />
      </div>
      <div className="relative isolate overflow-hidden flex-1 grid place-items-center px-4 py-12">
        <span className="pontos -z-10" aria-hidden />
        <div className="flex flex-col items-center gap-3 text-center">
          <Construction size={24} strokeWidth={1.5} aria-hidden className="text-fg-muted" />
          <h1 className="m-0 text-[18px] leading-[26px] font-semibold">Esta etapa ainda não está disponível</h1>
          <p className="m-0 max-w-[40ch] text-fg-muted">Sua sessão está salva e continua daqui quando a etapa ficar pronta.</p>
        </div>
      </div>
    </div>
  );
}
