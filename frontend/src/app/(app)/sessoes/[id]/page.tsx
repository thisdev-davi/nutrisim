import { Header } from "@/components/ui/Header";
import { StageSwitcher } from "./StageSwitcher";

export default async function SessaoPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const resolvedParams = await params;
  const sessaoId = resolvedParams.id;

  return (
    <div className="min-h-screen bg-bg text-fg font-sans flex flex-col">
      <main className="w-full max-w-[1100px] mx-auto p-4 md:py-10 md:px-8 flex-1 flex flex-col gap-6 md:gap-8">
        
        <header className="flex flex-col gap-1">
          <h1 className="font-display text-[24px] md:text-[28px] font-bold text-fg">
            Consulta em Andamento
          </h1>
          <p className="font-mono text-[12px] md:text-[13px] text-fg-muted uppercase tracking-[0.04em]">
            ID da Sessão: {sessaoId}
          </p>
        </header>

        <StageSwitcher sessaoId={sessaoId} />

      </main>
    </div>
  );
}