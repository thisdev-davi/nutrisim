"use client";

import { useSessao } from "./AnamneseChat";
import { EncerrarAnamnese } from "./EncerrarAnamnese";

export function AnamneseInstructions({ sessaoId }: { sessaoId: string }) {
  const etapa = useSessao(sessaoId).data?.etapa;

  return (
    <aside className="w-full bg-surface border border-line rounded-lg p-6 flex flex-col gap-6 lg:sticky lg:top-8">
      <h2 className="m-0 text-[18px] font-semibold text-fg">Investigação clínica</h2>
      <div className="flex flex-col gap-4 text-[14px] leading-relaxed text-fg-muted">
        <p className="m-0">
          Nesta etapa, você está frente a frente com o paciente simulado. Conduza a entrevista de forma investigativa para extrair dados fundamentais.
        </p>
        <ul className="m-0 flex flex-col gap-2 list-disc pl-4 marker:text-line-strong">
          <li>Investigue a rotina de trabalho e os horários das refeições.</li>
          <li>Identifique aversões, intolerâncias e o limite financeiro.</li>
          <li>Pergunte sobre consumo de água, sono e recordatório 24h.</li>
        </ul>
        <p className="m-0">
          Quando tiver todas as informações necessárias para calcular o Gasto Energético e montar as refeições, encerre a entrevista para prosseguir.
        </p>
      </div>

      <div className="pt-6 border-t border-line">
        <EncerrarAnamnese sessaoId={sessaoId} disabled={etapa !== "anamnese"} />
      </div>
    </aside>
  );
}
