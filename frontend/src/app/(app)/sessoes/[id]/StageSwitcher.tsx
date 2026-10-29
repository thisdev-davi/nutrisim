"use client";

import { useState } from "react";
import { AnamneseChat } from "./_anamnese/AnamneseChat";
import { AnamneseInstructions } from "./_anamnese/AnamneseInstructions";
import { SidebarStages } from "./SidebarStages";
import { Button } from "@/components/ui/Button";

type EtapaSessao = "anamnese" | "plano";

export function StageSwitcher({ sessaoId }: { sessaoId: string }) {
  const [etapaAtual, setEtapaAtual] = useState<EtapaSessao>("anamnese");

  return (
    <div className="flex flex-col lg:grid lg:grid-cols-[1.3fr_1fr] gap-6 items-start">
      
      {etapaAtual === "anamnese" && (
        <>
          <div className="w-full">
            <AnamneseChat sessaoId={sessaoId} />
          </div>
          <AnamneseInstructions onAvancar={() => setEtapaAtual("plano")} />
        </>
      )}

      {etapaAtual === "plano" && (
        <>
          <div className="w-full h-[85dvh] md:h-[600px] border border-line rounded-xl bg-surface flex items-center justify-center text-fg-muted p-8 text-center">
            Interface do Plano Alimentar (Em construção...)
          </div>
          
          <SidebarStages
            etapaAtual={3}
            totalEtapas={5}
            nomeEtapa="Plano Alimentar"
            titulo="Cálculo e Refeições"
          >
            <div className="flex flex-col gap-4 text-[14px] leading-relaxed text-fg-muted">
              <p>
                Utilize os dados coletados na anamnese para estipular o Gasto Energético Total e distribuir os macronutrientes.
              </p>
            </div>

            <div className="pt-6 border-t border-line mt-2 flex flex-col gap-3">
              <Button type="button" className="w-full" disabled>
                Finalizar Plano
              </Button>
              <Button 
                type="button" 
                variant="ghost" 
                className="w-full" 
                onClick={() => setEtapaAtual("anamnese")}
              >
                Voltar para Anamnese
              </Button>
            </div>
          </SidebarStages>
        </>
      )}

    </div>
  );
}