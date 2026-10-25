"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { env } from "@/lib/env";

import { Header } from "@/components/ui/Header";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";

interface Perfil { id: string; nome: string; descricao: string; }
type Dificuldade = "facil" | "medio" | "dificil";
interface Opcoes { perfis: Perfil[]; dificuldades: Dificuldade[]; }
interface NovaSessao { perfil_id: string; dificuldade: Dificuldade; }
interface Sessao { id: string; etapa: string; perfil_id: string; dificuldade: Dificuldade; }

const ROTULOS_DIFICULDADE: Record<Dificuldade, string> = {
  facil: "Fácil",
  medio: "Média",
  dificil: "Difícil",
};

export default function NovoCasoPage() {
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const [perfilId, setPerfilId] = useState("");
  const [dificuldade, setDificuldade] = useState<Dificuldade | "">("");

  const { data: opcoes, isPending: carregandoOpcoes, error: erroCarregar, refetch: recarregarOpcoes } = useQuery({
    queryKey: ["perfis-e-dificuldades"],
    queryFn: async (): Promise<Opcoes> => {
      const resp = await fetch(`${env.api.url}/api/perfis`);
      if (!resp.ok) throw new Error("Não foi possível carregar os perfis disponíveis.");
      return resp.json();
    },
  });

  const { mutate: gerarCaso, isPending: gerandoCaso, error: erroCriar, reset: limparErroCriar } = useMutation({
    mutationFn: async (dados: NovaSessao): Promise<Sessao> => {
      const resp = await fetch(`${env.api.url}/api/sessoes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });
      if (!resp.ok) {
        const errorBody = await resp.json().catch(() => null);
        throw new Error(errorBody?.erro?.mensagem || "Falha ao criar o caso clínico.");
      }
      return resp.json();
    },
    onSuccess: (sessao) => router.push(`/sessoes/${sessao.id}`),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!perfilId || !dificuldade || gerandoCaso) return;
    limparErroCriar();
    gerarCaso({ perfil_id: perfilId, dificuldade: dificuldade as Dificuldade });
  }

  const podeCriar = perfilId !== "" && dificuldade !== "" && !gerandoCaso;
  const perfilSelecionado = opcoes?.perfis.find((p) => p.id === perfilId);

  // Define se a interface inicial está carregando
  const carregandoInterface = !mounted || carregandoOpcoes;

  return (
    <div className="min-h-screen bg-bg text-fg font-sans flex flex-col">
      
      <Header mobileTitle="Configurar Paciente" activeMenu="casos" />

      <main className="w-full max-w-[900px] mx-auto p-5 md:py-12 md:px-8 flex-1">
        
        <h1 className="md:hidden text-[20px] font-bold text-fg mb-6">Parâmetros da Simulação</h1>
        <h1 className="hidden md:block font-display text-[28px] font-bold text-fg mb-10 text-center md:text-left">
          Configurar Novo Paciente (Gerado por IA)
        </h1>

        <div className="flex flex-col md:grid md:grid-cols-[1fr_1fr] gap-6 md:gap-10 items-start">
          
          <div className="w-full">
            {carregandoInterface ? (
              /* Estado de Carregamento (Skeleton) */
              <div className="flex flex-col gap-5 w-full animate-pulse">
                <div className="flex flex-col gap-1.5">
                  <div className="h-4 w-32 bg-line-strong/20 rounded-sm"></div>
                  <div className="h-11 w-full bg-surface-raised rounded-md"></div>
                </div>
                <div className="flex flex-col gap-1.5">
                  <div className="h-4 w-24 bg-line-strong/20 rounded-sm"></div>
                  <div className="h-11 w-full bg-surface-raised rounded-md"></div>
                </div>
                <div className="h-11 w-full bg-surface-raised rounded-md mt-2"></div>
              </div>
            ) : erroCarregar ? (
              /* Estado de Erro de Conexão */
              <Alert 
                type="danger" 
                title="Falha de comunicação" 
                action={
                  <button 
                    onClick={() => recarregarOpcoes()} 
                    className="text-[13px] font-medium underline hover:opacity-80 transition-opacity"
                  >
                    Tentar buscar novamente
                  </button>
                }
              >
                Não foi possível conectar ao servidor para carregar os perfis clínicos. Verifique sua conexão ou tente novamente em instantes.
              </Alert>
            ) : (
              /* Formulário Carregado */
              <form onSubmit={handleSubmit} className="flex flex-col gap-5 w-full">
                <Select
                  id="perfil"
                  label="Patologia/Objetivo"
                  value={perfilId}
                  onChange={(e) => setPerfilId(e.target.value)}
                  disabled={gerandoCaso}
                  required
                  helpText={perfilSelecionado?.descricao}
                >
                  <option value="">Selecione...</option>
                  {opcoes?.perfis.map((p) => (
                    <option key={p.id} value={p.id}>{p.nome}</option>
                  ))}
                </Select>

                <Select
                  id="dificuldade"
                  label="Dificuldade"
                  value={dificuldade}
                  onChange={(e) => setDificuldade(e.target.value as Dificuldade)}
                  disabled={gerandoCaso}
                  required
                >
                  <option value="">Selecione...</option>
                  {opcoes?.dificuldades.map((d) => (
                    <option key={d} value={d}>{ROTULOS_DIFICULDADE[d]}</option>
                  ))}
                </Select>

                <div className="md:hidden mt-2">
                  <Alert type="info">
                    A IA criará um perfil único (história, rotina, gostos) com base nas suas escolhas. Descubra os detalhes conversando com ele na anamnese!
                  </Alert>
                </div>

                {erroCriar && (
                  <div className="mt-2">
                    <Alert type="danger" action={
                      <button type="button" onClick={() => { limparErroCriar(); handleSubmit({ preventDefault: () => {} } as React.FormEvent); }} className="text-[13px] font-medium">
                        Tentar de novo
                      </button>
                    }>
                      {erroCriar instanceof Error ? erroCriar.message : "Erro ao criar."}
                    </Alert>
                  </div>
                )}

                <Button type="submit" disabled={!podeCriar} className="mt-2 w-full">
                  {gerandoCaso ? "Gerando paciente..." : (
                    <><span className="md:hidden">Gerar Paciente e Iniciar</span><span className="hidden md:inline">Gerar Ficha Oculta e Iniciar Consulta</span></>
                  )}
                </Button>
              </form>
            )}
          </div>

          <aside className="hidden md:flex flex-col border border-line bg-surface rounded-lg p-6 xl:p-8 h-fit gap-4 w-full">
            <h2 className="text-[18px] font-semibold text-fg">Como funciona a geração?</h2>
            <div className="flex flex-col gap-4 text-[14px] leading-6 text-fg-muted">
              <p>Ao clicar em 'Gerar Ficha Oculta', nossa Inteligência Artificial irá estruturar um paciente exclusivo contendo uma história de vida, rotina de trabalho, limitações financeiras e resistências alimentares.</p>
              <p>Você não verá esses dados previamente. O objetivo é testar suas habilidades investigativas conversando com ele em tempo real durante a etapa de Anamnese, como em um consultório de verdade.</p>
            </div>
          </aside>

        </div>
      </main>
    </div>
  );
}