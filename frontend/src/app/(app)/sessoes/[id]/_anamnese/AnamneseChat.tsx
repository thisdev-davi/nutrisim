"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Send, Sparkles } from "lucide-react";
import { api, type Erro } from "@/lib/api";
import { enviarMensagem } from "@/lib/sse";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";

export interface Mensagem {
  id: string;
  autor: "estudante" | "paciente";
  texto: string;
}

export interface Sessao {
  id: string;
  etapa: string;
  paciente: { nome: string; idade: number; queixa_principal: string };
  mensagens: Mensagem[];
}

const LIMITE = 2000; // o mesmo do backend (dados_invalidos acima disso)

export const chaveSessao = (id: string) => ["sessao", id];

const consultaSessao = (id: string) => ({ queryKey: chaveSessao(id), queryFn: () => api<Sessao>(`/sessoes/${id}`) });

export function useSessao(id: string) {
  return useQuery({ ...consultaSessao(id), retry: false });
}

export function AnamneseChat({ sessaoId }: { sessaoId: string }) {
  const queryClient = useQueryClient();
  const [textoInput, setTextoInput] = useState("");
  // null fora do stream; "" enquanto o paciente ainda nao mandou trecho
  const [streaming, setStreaming] = useState<string | null>(null);
  const [falha, setFalha] = useState<{ erro: Erro; texto: string } | null>(null);

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const { data: sessao, isPending, error, refetch } = useSessao(sessaoId);
  const mensagens = sessao?.mensagens ?? [];
  const aberta = sessao?.etapa === "anamnese";

  // sair da tela cancela o stream em andamento
  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    const area = scrollAreaRef.current;
    if (area) area.scrollTop = area.scrollHeight;
  }, [sessao, streaming]);

  useEffect(() => {
    if (streaming === null && sessao) inputRef.current?.focus();
  }, [streaming, sessao]);

  function acrescentar(mensagem: Mensagem) {
    queryClient.setQueryData<Sessao>(chaveSessao(sessaoId), (s) => s && { ...s, mensagens: [...s.mensagens, mensagem] });
  }

  async function enviar(texto: string) {
    const controle = new AbortController();
    abortRef.current = controle;
    setFalha(null);
    setStreaming("");
    acrescentar({ id: `temp-${Date.now()}`, autor: "estudante", texto });
    let parcial = "";
    try {
      const id = await enviarMensagem(sessaoId, texto, (trecho) => setStreaming((parcial += trecho)), controle.signal);
      acrescentar({ id, autor: "paciente", texto: parcial });
    } catch (e) {
      if (controle.signal.aborted) return;
      // o backend e a fonte da verdade: a pergunta e a fala podem ter sido salvas antes da queda
      const atual = await queryClient.fetchQuery({ ...consultaSessao(sessaoId), staleTime: 0 }).catch(() => null);
      const [pergunta, resposta] = atual?.mensagens.slice(-2) ?? [];
      if (resposta?.autor === "paciente" && pergunta?.texto === texto) return;
      if (!atual) {
        queryClient.setQueryData<Sessao>(chaveSessao(sessaoId), (s) => s && { ...s, mensagens: s.mensagens.filter((m) => !m.id.startsWith("temp-")) });
      }
      setFalha({ erro: e as Erro, texto });
    } finally {
      if (!controle.signal.aborted) setStreaming(null);
    }
  }

  function handleEnviar(e: React.FormEvent) {
    e.preventDefault();
    const texto = textoInput.trim();
    if (!texto || streaming !== null) return;
    setTextoInput("");
    enviar(texto);
  }

  if (isPending) {
    return (
      <div className="flex items-center justify-center h-[70dvh] md:h-[600px] w-full border border-line rounded-lg bg-surface text-fg-muted">
        Buscando dados do paciente e histórico...
      </div>
    );
  }

  if (error || !sessao) {
    const erro = error as unknown as Erro;
    return (
      <Alert
        type="danger"
        action={
          erro.codigo === "sessao_nao_encontrada" ? (
            <Link href="/caso/novo" className="text-[13px] font-medium underline">Começar um novo caso</Link>
          ) : (
            <button type="button" onClick={() => refetch()} className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>
          )
        }
      >
        {erro.mensagem ?? "Não foi possível carregar o chat da consulta."}
      </Alert>
    );
  }

  const nomePaciente = sessao.paciente.nome;
  const inicialPaciente = nomePaciente.charAt(0).toUpperCase();

  return (
    <div className="flex flex-col h-[70dvh] md:h-[600px] w-full border border-line rounded-lg overflow-hidden bg-surface">
      <div className="bg-surface border-b border-line p-4 shrink-0 flex flex-col gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="m-0 font-semibold text-fg text-[18px] leading-[26px]">
            {nomePaciente}, {sessao.paciente.idade} anos
          </h2>
          <span className="shrink-0 whitespace-nowrap inline-flex items-center h-6 px-[10px] gap-[6px] rounded-full bg-accent-soft text-accent text-[12px] font-medium leading-none">
            <Sparkles size={12} strokeWidth={1.5} aria-hidden />
            Paciente simulado por IA
          </span>
        </div>
        <p className="m-0 font-mono text-[12px] leading-[16px] text-fg-muted uppercase tracking-[0.04em]">
          <span className="font-semibold text-fg">Queixa:</span> {sessao.paciente.queixa_principal}
        </p>
      </div>

      <div ref={scrollAreaRef} role="log" aria-live="polite" className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-bg/50 scroll-smooth motion-reduce:scroll-auto">
        {mensagens.map((msg) => {
          const isPatient = msg.autor === "paciente";
          return (
            <div key={msg.id} className={`max-w-[85%] md:max-w-[80%] flex ${isPatient ? "self-start gap-3" : "self-end flex-col items-end gap-1"}`}>
              {isPatient && (
                <div className="w-8 h-8 rounded-full border border-line-strong bg-surface flex items-center justify-center font-mono text-[12px] font-medium text-fg-muted shrink-0" aria-hidden="true">
                  {inicialPaciente}
                </div>
              )}
              <div className="flex flex-col gap-1 w-full">
                <div className={`px-[14px] py-[10px] text-[15px] leading-[24px] break-words ${isPatient ? "bg-surface border border-line rounded-lg rounded-bl-[4px] text-fg" : "bg-surface-raised rounded-lg rounded-br-[4px] text-fg"}`}>
                  {msg.texto}
                </div>
                <span className="font-mono text-[12px] leading-[16px] text-fg-muted uppercase tracking-[0.04em]">
                  {isPatient ? nomePaciente : "Você"}
                </span>
              </div>
            </div>
          );
        })}

        {streaming !== null && (
          <div className="self-start max-w-[85%] md:max-w-[80%] flex gap-3" aria-busy="true">
            <div className="w-8 h-8 rounded-full border border-line-strong bg-surface flex items-center justify-center font-mono text-[12px] font-medium text-fg-muted shrink-0" aria-hidden="true">
              {inicialPaciente}
            </div>
            <div className="flex flex-col gap-1 w-full">
              <div className="bg-surface border border-line px-[14px] py-[10px] rounded-lg rounded-bl-[4px] text-[15px] leading-[24px] text-fg break-words">
                <span className="sr-only">O paciente está respondendo...</span>
                <span aria-hidden="true">{streaming}</span>
                <span aria-hidden="true" className="inline-block w-2 h-[18px] ml-1 bg-fg align-middle animate-[pulse_1s_steps(1)_infinite] motion-reduce:animate-none" />
              </div>
              <span className="font-mono text-[12px] leading-[16px] text-fg-muted uppercase tracking-[0.04em]">
                {nomePaciente} respondendo...
              </span>
            </div>
          </div>
        )}
      </div>

      {falha && (
        <div className="px-2 pt-2 md:px-3">
          <Alert
            type="danger"
            action={
              <button type="button" onClick={() => enviar(falha.texto)} className="text-[13px] font-medium underline cursor-pointer">
                Tentar de novo
              </button>
            }
          >
            {falha.erro.mensagem}
          </Alert>
        </div>
      )}

      {!aberta && (
        <div className="px-2 pt-2 md:px-3">
          <Alert type="info">A anamnese foi encerrada. O plano alimentar chega na próxima etapa.</Alert>
        </div>
      )}

      <form onSubmit={handleEnviar} className="flex gap-2 p-2 md:p-3 bg-surface border-t border-line shrink-0 w-full overflow-hidden">
        <label htmlFor="composer-input" className="sr-only">
          Mensagem para o paciente
        </label>
        <input
          id="composer-input"
          ref={inputRef}
          type="text"
          value={textoInput}
          onChange={(e) => setTextoInput(e.target.value)}
          disabled={streaming !== null || !aberta}
          maxLength={LIMITE}
          placeholder="Escreva sua mensagem..."
          className="flex-1 min-w-0 h-11 px-3 border border-line-strong rounded-md bg-bg text-fg text-[16px] md:text-[15px] leading-6 placeholder:text-fg-muted focus:outline-focus focus:outline-2 disabled:opacity-45 disabled:cursor-not-allowed transition-colors hover:border-fg-muted"
          autoComplete="off"
        />
        <Button type="submit" variant="secondary" disabled={!textoInput.trim() || streaming !== null || !aberta} aria-label="Enviar mensagem" className="w-11 px-0 shrink-0">
          <Send size={16} strokeWidth={1.5} aria-hidden />
        </Button>
      </form>
    </div>
  );
}
