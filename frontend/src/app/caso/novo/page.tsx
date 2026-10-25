"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Sparkle } from "lucide-react";
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

const CONTEUDO_FICHA = ["História de vida", "Rotina de trabalho", "Limitações financeiras", "Resistências alimentares"];
const ETAPAS = ["Caso", "Anamnese", "Plano alimentar", "Cenários de adesão", "Retorno e feedback"];

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
  const carregandoInterface = !mounted || carregandoOpcoes;

  return (
    <div className="min-h-screen bg-bg text-fg font-sans flex flex-col">
      <Header activeMenu="casos" />

      <main className="w-full max-w-[1040px] mx-auto px-4 py-6 md:pt-8 md:px-6 md:pb-12 flex-1 flex flex-col gap-8">
        <div className="flex flex-col items-start gap-3">
          <span className="font-mono text-[12px] leading-4 font-medium tracking-[0.04em] uppercase text-fg-muted">
            Etapa 1 de 5 · Caso
          </span>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="font-display text-[24px] leading-[30px] md:text-[32px] md:leading-[38px] font-semibold tracking-[-0.02em] text-balance">
              Configurar novo paciente
            </h1>
            <span className="inline-flex items-center h-6 px-2.5 gap-1.5 rounded-full bg-accent-soft text-accent text-[12px] font-medium">
              <Sparkle size={12} strokeWidth={1.5} aria-hidden />
              Gerado por IA
            </span>
          </div>
          <p className="max-w-[62ch] text-fg-muted">
            Escolha os parâmetros da simulação. A IA cria um paciente único a partir deles, e você descobre os detalhes conversando com ele na anamnese.
          </p>
        </div>

        <div className="flex flex-col gap-6 lg:grid lg:grid-cols-[minmax(0,1fr)_300px] lg:items-start">
          <section aria-labelledby="parametros" className="flex flex-col gap-4 md:p-6 md:border md:border-line md:bg-surface md:rounded-lg">
            <h2 id="parametros" className="text-[18px] leading-[26px] font-semibold">Parâmetros da simulação</h2>
            {carregandoInterface ? (
              <div className="grid md:grid-cols-2 gap-4 animate-pulse" aria-busy="true">
                <div className="h-[66px] bg-surface-raised rounded-md"></div>
                <div className="h-[66px] bg-surface-raised rounded-md"></div>
              </div>
            ) : erroCarregar ? (
              <Alert
                type="danger"
                title="Falha de comunicação"
                action={
                  <button
                    onClick={() => recarregarOpcoes()}
                    className="text-[13px] font-medium underline hover:opacity-80 transition-opacity cursor-pointer"
                  >
                    Tentar buscar novamente
                  </button>
                }
              >
                Não foi possível carregar os perfis clínicos. Verifique sua conexão e tente de novo.
              </Alert>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <Select
                    id="perfil"
                    label="Patologia ou objetivo"
                    value={perfilId}
                    onChange={(e) => setPerfilId(e.target.value)}
                    disabled={gerandoCaso}
                    required
                    helpText={perfilSelecionado?.descricao}
                  >
                    <option value="">Selecione…</option>
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
                    <option value="">Selecione…</option>
                    {opcoes?.dificuldades.map((d) => (
                      <option key={d} value={d}>{ROTULOS_DIFICULDADE[d]}</option>
                    ))}
                  </Select>
                </div>

                <Alert type="info">
                  A IA cria história, rotina e gostos com base nas suas escolhas. Nada disso aparece antes da consulta.
                </Alert>

                {erroCriar && (
                  <Alert type="danger" action={
                    <button type="submit" className="text-[13px] font-medium underline hover:opacity-80 transition-opacity cursor-pointer">
                      Tentar de novo
                    </button>
                  }>
                    {erroCriar instanceof Error ? erroCriar.message : "Erro ao criar."}
                  </Alert>
                )}

                <div className="flex flex-col md:flex-row gap-3 pt-4 border-t border-line">
                  <Button type="submit" disabled={!podeCriar}>
                    {gerandoCaso ? "Gerando paciente…" : (
                      <>
                        <Sparkle size={16} strokeWidth={1.5} aria-hidden />
                        <span className="md:hidden">Gerar paciente e iniciar</span>
                        <span className="hidden md:inline">Gerar ficha oculta e iniciar consulta</span>
                      </>
                    )}
                  </Button>
                  <Button type="button" variant="ghost" onClick={() => router.back()}>
                    Cancelar
                  </Button>
                </div>
              </form>
            )}
          </section>

          <aside aria-labelledby="como-funciona" className="flex flex-col gap-4 pt-6 border-t border-line md:p-6 md:border md:bg-surface md:rounded-lg lg:py-2 lg:pr-0 lg:pl-6 lg:border-0 lg:border-l lg:bg-transparent lg:rounded-none">
            <h2 id="como-funciona" className="text-[18px] leading-[26px] lg:text-[15px] lg:leading-6 font-semibold">Como funciona a geração?</h2>
            <p className="text-fg-muted lg:text-[13px] lg:leading-5">
              Ao gerar a ficha oculta, a IA estrutura um paciente exclusivo. Você não vê esses dados antes: precisa descobri-los na anamnese, como num consultório de verdade.
            </p>
            <ul aria-label="O que a ficha oculta contém" className="flex flex-wrap gap-2">
              {CONTEUDO_FICHA.map((item) => (
                <li key={item} className="inline-flex items-center h-6 px-2.5 rounded-full border border-line-strong text-fg-muted text-[12px] font-medium">
                  {item}
                </li>
              ))}
            </ul>
            <ol aria-label="Etapas da simulação" className="grid gap-2 pt-4 border-t border-line">
              {ETAPAS.map((etapa, i) => (
                <li key={etapa} aria-current={i === 0 ? "step" : undefined} className={`grid grid-cols-[24px_1fr] items-center gap-3 text-[14px] leading-5 ${i === 0 ? "text-fg font-medium" : "text-fg-muted"}`}>
                  <span className={`grid place-items-center size-6 rounded-full border font-mono text-[12px] font-medium ${i === 0 ? "border-transparent bg-fg text-bg" : "border-line-strong"}`}>
                    {i + 1}
                  </span>
                  {etapa}
                </li>
              ))}
            </ol>
          </aside>
        </div>
      </main>
    </div>
  );
}
