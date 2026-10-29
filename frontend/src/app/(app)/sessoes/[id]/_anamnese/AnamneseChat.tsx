"use client";

import { useState, useRef, useEffect, type ReactNode } from "react";
import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { NotebookPen, Search, Send, Sparkle } from "lucide-react";
import { api, type Erro } from "@/lib/api";
import { enviarMensagem } from "@/lib/sse";
import { estiloBotao } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { Avatar } from "@/components/ui/Avatar";
import { Etapas } from "@/components/ui/Etapas";
import { Anotacoes, ICONE } from "./Anotacoes";
import { EncerrarAnamnese } from "./EncerrarAnamnese";

export interface Mensagem {
  id: string;
  autor: "estudante" | "paciente";
  texto: string;
  criada_em: string;
}

export interface Sessao {
  id: string;
  etapa: string;
  perfil_id: string;
  dificuldade: "facil" | "medio" | "dificil";
  paciente: { nome: string; idade: number; queixa_principal: string };
  mensagens: Mensagem[];
}

const LIMITE = 2000; // o mesmo do backend (dados_invalidos acima disso)

const DIFICULDADE = { facil: "fácil", medio: "média", dificil: "difícil" };

const hora = (iso: string) => new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

export const chaveSessao = (id: string) => ["sessao", id];

const consultaSessao = (id: string) => ({ queryKey: chaveSessao(id), queryFn: () => api<Sessao>(`/sessoes/${id}`) });

export function useSessao(id: string) {
  return useQuery({ ...consultaSessao(id), retry: false });
}

function Fala({ nome, meta, ocupado, children }: { nome?: string; meta: string; ocupado?: boolean; children: ReactNode }) {
  const paciente = Boolean(nome);
  return (
    <div className={`flex items-end gap-3 max-w-[80%] ${paciente ? "self-start" : "self-end flex-row-reverse"}`}>
      {nome && <Avatar nome={nome} />}
      <div className={`flex flex-col gap-2 min-w-0 ${paciente ? "" : "items-end"}`}>
        <div
          aria-busy={ocupado || undefined}
          className={`px-[14px] py-[10px] border rounded-[14px] text-[15px] leading-6 [overflow-wrap:anywhere] whitespace-pre-wrap ${paciente ? "border-line bg-surface rounded-bl-[4px]" : "border-transparent bg-surface-raised rounded-br-[4px]"}`}
        >
          {children}
        </div>
        <span className="font-mono text-[12px] leading-4 text-fg-muted">{meta}</span>
      </div>
    </div>
  );
}

export function AnamneseChat({ sessaoId }: { sessaoId: string }) {
  const queryClient = useQueryClient();
  const [textoInput, setTextoInput] = useState("");
  // null fora do stream; "" enquanto o paciente ainda nao mandou trecho
  const [streaming, setStreaming] = useState<string | null>(null);
  const [falhou, setFalhou] = useState(false);
  const [painel, setPainel] = useState(false);

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const { data: sessao, error, refetch } = useSessao(sessaoId);
  const { data: opcoes } = useQuery({ queryKey: ["perfis-e-dificuldades"], queryFn: () => api<{ perfis?: { id: string; nome: string }[] }>("/perfis") });
  const mensagens = sessao?.mensagens ?? [];
  const aberta = sessao?.etapa === "anamnese";

  // sair da tela cancela o stream em andamento
  useEffect(() => () => abortRef.current?.abort(), []);

  // anotacoes abertas no desktop; no celular cobririam o chat
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (matchMedia("(min-width: 768px)").matches) setPainel(true);
  }, []);

  useEffect(() => {
    const area = scrollAreaRef.current;
    if (area) area.scrollTop = area.scrollHeight;
  }, [sessao, streaming]);

  useEffect(() => {
    if (streaming === null && sessao) inputRef.current?.focus();
  }, [streaming, sessao]);

  function acrescentar(mensagem: Omit<Mensagem, "criada_em">) {
    const nova = { ...mensagem, criada_em: new Date().toISOString() };
    queryClient.setQueryData<Sessao>(chaveSessao(sessaoId), (s) => s && { ...s, mensagens: [...s.mensagens, nova] });
  }

  async function enviar(texto: string) {
    const controle = new AbortController();
    abortRef.current = controle;
    setFalhou(false);
    setStreaming("");
    acrescentar({ id: `temp-${Date.now()}`, autor: "estudante", texto });
    let parcial = "";
    try {
      const id = await enviarMensagem(sessaoId, texto, (trecho) => setStreaming((parcial += trecho)), controle.signal);
      acrescentar({ id, autor: "paciente", texto: parcial });
    } catch {
      if (controle.signal.aborted) return;
      // o backend e a fonte da verdade: a pergunta e a fala podem ter sido salvas antes da queda
      const atual = await queryClient.fetchQuery({ ...consultaSessao(sessaoId), staleTime: 0 }).catch(() => null);
      const [pergunta, resposta] = atual?.mensagens.slice(-2) ?? [];
      if (resposta?.autor === "paciente" && pergunta?.texto === texto) return;
      if (!atual) {
        queryClient.setQueryData<Sessao>(chaveSessao(sessaoId), (s) => s && { ...s, mensagens: s.mensagens.filter((m) => !m.id.startsWith("temp-")) });
      }
      // a pergunta volta para o campo, pronta para reenviar
      setTextoInput(texto);
      setFalhou(true);
    } finally {
      if (!controle.signal.aborted) setStreaming(null);
    }
  }

  function fecharPainel() {
    setPainel(false);
    // o foco volta ao botao visivel que abre o painel (o do topo no celular, o da lateral no desktop)
    requestAnimationFrame(() => [...document.querySelectorAll<HTMLElement>('[aria-controls="anotacoes"]')].find((b) => b.offsetParent)?.focus());
  }

  function submeter() {
    const texto = textoInput.trim();
    if (!texto || streaming !== null) return;
    setTextoInput("");
    enviar(texto);
  }

  if (error) {
    const erro = error as unknown as Erro;
    if (erro.codigo === "sessao_nao_encontrada") {
      return (
        <div className="relative isolate overflow-hidden flex-1 grid place-items-center px-4 py-12">
          <span className="pontos -z-10" aria-hidden />
          <div className="flex flex-col items-center gap-3 text-center">
            <Search size={24} strokeWidth={1.5} aria-hidden className="text-fg-muted" />
            <h1 className="m-0 text-[18px] leading-[26px] font-semibold">Sessão não encontrada</h1>
            <p className="m-0 max-w-[40ch] text-fg-muted">O link pode estar errado ou a sessão é de outra conta.</p>
            <Link href="/caso/novo" className={estiloBotao("primary", true)}>Começar novo caso</Link>
          </div>
        </div>
      );
    }
    return (
      <div className="w-full max-w-[720px] mx-auto px-4 py-8">
        <Alert
          type="danger"
          action={<button type="button" onClick={() => refetch()} className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>}
        >
          {erro.mensagem ?? "Não foi possível carregar a conversa."}
        </Alert>
      </div>
    );
  }

  const nome = sessao?.paciente.nome ?? "";
  const perfil = opcoes?.perfis?.find((p) => p.id === sessao?.perfil_id)?.nome;

  return (
    <div className="flex-1 min-h-0 flex">
      <div className="flex-1 min-w-0 flex flex-col">
        <Etapas atual={2} compacta />
        <div className="flex items-center gap-3 px-4 py-2 md:px-8 md:py-4 border-b border-line">
          <Etapas atual={2} />
          <div className="ml-auto flex items-center gap-1">
            <button type="button" className={`${ICONE} md:hidden`} aria-controls="anotacoes" aria-expanded={painel} aria-label="Abrir anotações" onClick={() => setPainel(true)}>
              <NotebookPen size={16} strokeWidth={1.5} aria-hidden />
            </button>
            <EncerrarAnamnese sessaoId={sessaoId} disabled={streaming !== null || !aberta} />
          </div>
        </div>

        {/* relative: o sr-only (absolute) do "digitando" fica preso aqui e nao estica a pagina */}
        <div ref={scrollAreaRef} className="relative flex-1 min-h-0 overflow-y-auto px-4 pt-4 pb-4 md:px-6 md:pt-8 scroll-smooth motion-reduce:scroll-auto">
          <div className="w-full max-w-[720px] mx-auto flex flex-col gap-6">
            {/* carregando: a moldura e a mesma, so a conversa vira bloco */}
            {!sessao ? (
              <div aria-busy="true" aria-label="Carregando a conversa" className="flex flex-col gap-4">
                <div className="h-11 w-[60%] self-end rounded-lg bg-surface-raised" />
                <div className="h-[68px] w-[75%] rounded-lg bg-surface-raised" />
                <div className="h-11 w-[45%] self-end rounded-lg bg-surface-raised" />
              </div>
            ) : (
            <>
            <div className="flex flex-col items-start gap-2 p-5 border border-line rounded-lg">
              <div className="flex items-center gap-3">
                <Avatar nome={nome} />
                <div className="flex flex-col">
                  <span className="text-[15px] leading-[22px] font-semibold">{nome}, {sessao.paciente.idade} anos</span>
                  <span className="text-[13px] leading-5 text-fg-muted">
                    {perfil && `${perfil} · `}Dificuldade {DIFICULDADE[sessao.dificuldade]}
                  </span>
                </div>
              </div>
              <span className="inline-flex items-center gap-[6px] h-6 px-[10px] rounded-full bg-accent-soft text-accent text-[12px] font-medium leading-none whitespace-nowrap">
                <Sparkle size={12} strokeWidth={1.5} aria-hidden />
                Paciente simulado por IA
              </span>
              <span className="text-[13px] leading-5 font-medium text-fg-muted">Queixa principal</span>
              <p className="m-0">{sessao.paciente.queixa_principal}</p>
              {mensagens.length === 0 && <p className="m-0 text-[13px] leading-5 text-fg-muted">Apresente-se e pergunte o motivo da consulta.</p>}
            </div>

            <div role="log" aria-live="polite" aria-label={`Conversa com ${nome}`} className="flex flex-col gap-4">
              {mensagens.map((msg) =>
                msg.autor === "paciente" ? (
                  <Fala key={msg.id} nome={nome} meta={`${nome} · ${hora(msg.criada_em)}`}>{msg.texto}</Fala>
                ) : (
                  <Fala key={msg.id} meta={hora(msg.criada_em)}>{msg.texto}</Fala>
                ),
              )}

              {streaming === "" && (
                <Fala nome={nome} meta={`${nome} está digitando…`} ocupado>
                  <span className="digitando" aria-hidden><span /><span /><span /></span>
                  <span className="sr-only">{nome} está digitando</span>
                </Fala>
              )}
              {streaming && (
                <Fala nome={nome} meta={`${nome} está respondendo…`} ocupado>
                  {streaming}
                  <span aria-hidden className="inline-block w-2 h-[18px] ml-0.5 align-[-3px] bg-fg animate-[pulse_1s_steps(1)_infinite] motion-reduce:animate-none" />
                </Fala>
              )}
            </div>
            </>
            )}
          </div>
        </div>

        <div className="px-3 pb-3 md:px-6 md:pb-6">
          <div className="w-full max-w-[720px] mx-auto flex flex-col gap-2">
            {falhou && (
              <Alert type="danger" action={<button type="button" onClick={submeter} disabled={!textoInput.trim()} className="text-[13px] font-medium underline cursor-pointer disabled:cursor-not-allowed disabled:opacity-45">Tentar de novo</button>}>
                O paciente não conseguiu responder agora. Sua pergunta continua no campo.
              </Alert>
            )}

            {!sessao || aberta ? (
              <>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    submeter();
                  }}
                  className="flex items-end gap-2 py-[6px] pr-[6px] pl-[18px] border border-line-strong rounded-xl bg-surface focus-within:border-transparent focus-within:outline-2 focus-within:outline-focus"
                >
                  <label htmlFor="pergunta" className="sr-only">Pergunta para o paciente</label>
                  <textarea
                    id="pergunta"
                    ref={inputRef}
                    rows={1}
                    value={textoInput}
                    onChange={(e) => setTextoInput(e.target.value)}
                    onKeyDown={(e) => {
                      // enter envia; shift+enter e a composicao do teclado (acentos) quebram a linha
                      if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                        e.preventDefault();
                        submeter();
                      }
                    }}
                    disabled={!sessao || streaming !== null}
                    maxLength={LIMITE}
                    placeholder="Escreva sua pergunta…"
                    className="flex-1 min-w-0 min-h-6 max-h-36 py-[6px] border-0 bg-transparent text-fg text-[16px] md:text-[15px] leading-6 resize-none [field-sizing:content] outline-none placeholder:text-fg-muted disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    aria-label="Enviar pergunta"
                    disabled={!textoInput.trim() || streaming !== null}
                    // a bolinha so aparece com texto; vazio fica so o icone
                    className={`grid place-items-center shrink-0 size-10 md:size-9 rounded-full transition-colors disabled:cursor-not-allowed ${textoInput.trim() ? "bg-fg text-bg cursor-pointer hover:bg-fg/85" : "text-fg-muted"}`}
                  >
                    <Send size={16} strokeWidth={1.5} aria-hidden />
                  </button>
                </form>
                <p className="hidden md:block m-0 text-[12px] leading-4 text-fg-muted">Enter envia · Shift+Enter quebra a linha</p>
              </>
            ) : (
              <Alert type="info">A anamnese foi encerrada. O plano alimentar chega na próxima etapa.</Alert>
            )}
          </div>
        </div>
      </div>

      <Anotacoes sessaoId={sessaoId} aberto={painel} onAbrir={() => setPainel(true)} onFechar={fecharPainel} />
    </div>
  );
}
