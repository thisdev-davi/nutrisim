"use client";

import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Send, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { env } from "@/lib/env";
import { fetchSSE } from "@/lib/sse";
import { Button } from "@/components/ui/Button";

export type Autor = "estudante" | "paciente";

export interface Mensagem {
  id: string;
  autor: Autor;
  texto: string;
}

export interface Paciente {
  nome: string;
  idade: number;
  queixa_principal: string;
}

export interface Sessao {
  id: string;
  etapa: string;
  perfil_id: string;
  dificuldade: string;
  paciente: Paciente;
  mensagens: Mensagem[];
}

interface ChatProps {
  sessaoId: string;
}

export function AnamneseChat({ sessaoId }: ChatProps) {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [textoInput, setTextoInput] = useState("");
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [textoStreaming, setTextoStreaming] = useState("");

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: sessao, isPending, isError } = useQuery({
    queryKey: ["sessao", sessaoId],
    queryFn: async (): Promise<Sessao> => {
      const { data } = await api.get<Sessao>(`/api/sessoes/${sessaoId}`);
      return data;
    },
    staleTime: Infinity, 
  });

  useEffect(() => {
    if (sessao?.mensagens) {
      setMensagens(sessao.mensagens);
    }
  }, [sessao]);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const area = scrollAreaRef.current;
      area.scrollTop = area.scrollHeight;
    }
  }, [mensagens, textoStreaming]);

  useEffect(() => {
    if (!isStreaming && !isPending && !isError) {
      inputRef.current?.focus();
    }
  }, [isStreaming, isPending, isError]);

  async function handleEnviar(e: React.FormEvent) {
    e.preventDefault();
    if (!textoInput.trim() || isStreaming) return;

    const novaMensagem: Mensagem = {
      id: `temp-${Date.now()}`,
      autor: "estudante",
      texto: textoInput.trim(),
    };

    setMensagens((prev) => [...prev, novaMensagem]);
    setTextoInput("");
    setIsStreaming(true);
    setTextoStreaming("");

    let textoAcumulado = "";

    await fetchSSE(`${env.api.url}/api/sessoes/${sessaoId}/mensagens`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: novaMensagem.texto }),
      
      onMessage: (evento) => {
        if (evento.event === "trecho") {
          const dados = JSON.parse(evento.data);
          textoAcumulado += dados.texto;
          setTextoStreaming(textoAcumulado);
        } else if (evento.event === "fim") {
          const dados = JSON.parse(evento.data);
          setMensagens((prev) => [
            ...prev,
            {
              id: `${dados.mensagem_id}-${Date.now()}`,
              autor: "paciente",
              texto: textoAcumulado,
            },
          ]);
          setIsStreaming(false);
          setTextoStreaming("");
        } else if (evento.event === "erro") {
          console.error("Erro da IA:", JSON.parse(evento.data));
          setIsStreaming(false);
        }
      },
      onError: (erro) => {
        console.error("Erro no streaming nativo:", erro);
        setIsStreaming(false);
      }
    });
  }

  if (isPending) {
    return (
      <div className="flex items-center justify-center h-[85dvh] md:h-[600px] w-full border border-line rounded-xl bg-surface text-fg-muted">
        Buscando dados do paciente e histórico...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center h-[85dvh] md:h-[600px] w-full border border-danger/30 rounded-xl bg-surface text-danger">
        Não foi possível carregar o chat da consulta.
      </div>
    );
  }

  const nomePaciente = sessao?.paciente?.nome || "Paciente";
  const inicialPaciente = nomePaciente.charAt(0).toUpperCase();

  return (
    <div className="flex flex-col h-[85dvh] md:h-[600px] w-full border border-line rounded-xl overflow-hidden bg-surface shadow-sm">
      
      {sessao?.paciente && (
        <div className="bg-surface border-b border-line p-4 shrink-0 z-10 flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-fg text-[18px] leading-[26px]">
              {nomePaciente}, {sessao.paciente.idade} anos
            </h3>
            <span className="shrink-0 whitespace-nowrap inline-flex items-center h-6 px-[10px] gap-[6px] rounded-full bg-accent-soft text-accent font-sans text-[12px] font-medium leading-none">
              <Sparkles size={12} strokeWidth={1.5} />
              Paciente simulado por IA
            </span>
          </div>
          <p className="font-mono text-[12px] leading-[16px] text-fg-muted uppercase tracking-[0.04em]">
            <span className="font-semibold text-fg">Queixa:</span> {sessao.paciente.queixa_principal}
          </p>
        </div>
      )}

      <div 
        ref={scrollAreaRef}
        role="log" 
        aria-live="polite"
        className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-bg/50 scroll-smooth"
      >
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
                <div className={`px-[14px] py-[10px] text-[15px] leading-[24px] break-words ${
                  isPatient 
                    ? "bg-surface border border-line rounded-lg rounded-bl-[4px] text-fg shadow-sm" 
                    : "bg-surface-raised rounded-lg rounded-br-[4px] text-fg"
                }`}>
                  {msg.texto}
                </div>
                
                <span className="font-mono text-[12px] leading-[16px] text-fg-muted uppercase tracking-[0.04em]">
                  {isPatient ? nomePaciente : "Você"}
                </span>
              </div>
            </div>
          );
        })}

        {isStreaming && (
          <div className="self-start max-w-[85%] md:max-w-[80%] flex gap-3" aria-busy="true">
            <div className="w-8 h-8 rounded-full border border-line-strong bg-surface flex items-center justify-center font-mono text-[12px] font-medium text-fg-muted shrink-0" aria-hidden="true">
              {inicialPaciente}
            </div>
            
            <div className="flex flex-col gap-1 w-full">
              <div className="bg-surface border border-line px-[14px] py-[10px] rounded-lg rounded-bl-[4px] text-[15px] leading-[24px] text-fg break-words shadow-sm">
                <span className="sr-only">O paciente está respondendo...</span>
                <span aria-hidden="true">{textoStreaming}</span>
                <span aria-hidden="true" className="inline-block w-2 h-[18px] ml-1 bg-fg align-middle animate-[pulse_1s_steps(1)_infinite]" />
              </div>
              <span className="font-mono text-[12px] leading-[16px] text-fg-muted uppercase tracking-[0.04em]">
                {nomePaciente} respondendo...
              </span>
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={handleEnviar}
        className="flex gap-2 p-2 md:p-3 bg-surface border-t border-line shrink-0 w-full overflow-hidden"
      >
        <label htmlFor="composer-input" className="sr-only">
          Mensagem para o paciente
        </label>
        
        <input
          id="composer-input"
          ref={inputRef}
          type="text"
          value={textoInput}
          onChange={(e) => setTextoInput(e.target.value)}
          disabled={isStreaming}
          placeholder="Escreva sua mensagem..."
          className="flex-1 min-w-0 h-11 px-3 border border-line-strong rounded-md bg-bg text-fg text-[16px] md:text-[15px] leading-6 placeholder:text-fg-muted focus:outline-focus focus:outline-2 disabled:opacity-45 disabled:cursor-not-allowed transition-colors hover:border-fg-muted"
          autoComplete="off"
        />
        
        <Button 
          type="submit" 
          variant="primary"
          disabled={!textoInput.trim() || isStreaming}
          aria-label="Enviar mensagem"
          className="w-11 px-0 shrink-0"
        >
          <Send size={20} strokeWidth={1.5} />
        </Button>
      </form>
    </div>
  );
}