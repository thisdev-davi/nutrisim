import { Button } from "@/components/ui/Button";
import { SidebarStages } from "../SidebarStages";

interface InstrucoesAnamneseProps {
  onAvancar: () => void;
}

export function AnamneseInstructions({ onAvancar }: InstrucoesAnamneseProps) {
  return (
    <SidebarStages
      etapaAtual={2}
      totalEtapas={5}
      nomeEtapa="Anamnese"
      titulo="Investigação Clínica"
    >
      <div className="flex flex-col gap-4 text-[14px] leading-relaxed text-fg-muted">
        <p>
          Nesta etapa, você está frente a frente com o paciente simulado. Conduza a entrevista de forma investigativa para extrair dados fundamentais.
        </p>
        <ul className="flex flex-col gap-2 list-disc pl-4 marker:text-line-strong">
          <li>Investigue a rotina de trabalho e os horários das refeições.</li>
          <li>Identifique aversões, intolerâncias e o limite financeiro.</li>
          <li>Pergunte sobre consumo de água, sono e recordatório 24h.</li>
        </ul>
        <p>
          Quando tiver todas as informações necessárias para calcular o Gasto Energético e montar as refeições, encerre a entrevista para prosseguir.
        </p>
      </div>

      <div className="pt-6 border-t border-line mt-2">
        <Button type="button" className="w-full" onClick={onAvancar}>
          Encerrar Anamnese e Criar Plano
        </Button>
      </div>
    </SidebarStages>
  );
}