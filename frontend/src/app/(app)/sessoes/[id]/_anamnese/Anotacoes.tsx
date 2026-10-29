"use client";

import { useState } from "react";
import { NotebookPen, X } from "lucide-react";

export const ICONE = "grid place-items-center size-11 md:size-8 rounded-md text-fg-muted transition-colors hover:bg-surface-raised hover:text-fg cursor-pointer";

const hora = (d: Date) => d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

// rascunho do estudante: fica so neste navegador, um por sessao
export function Anotacoes({ sessaoId, aberto, onAbrir, onFechar }: { sessaoId: string; aberto: boolean; onAbrir: () => void; onFechar: () => void }) {
  if (!aberto) {
    return (
      <nav aria-label="Anotações" className="hidden md:flex flex-none flex-col items-center w-[52px] py-3 border-l border-line">
        <button type="button" className={ICONE} aria-controls="anotacoes" aria-expanded={false} aria-label="Abrir anotações" title="Anotações" onClick={onAbrir}>
          <NotebookPen size={16} strokeWidth={1.5} aria-hidden />
        </button>
      </nav>
    );
  }
  return <Painel chave={`nutrisim:notas:${sessaoId}`} onFechar={onFechar} />;
}

// so monta no cliente (o painel comeca fechado), entao pode ler o localStorage direto
function Painel({ chave, onFechar }: { chave: string; onFechar: () => void }) {
  const [texto, setTexto] = useState(() => localStorage.getItem(chave) ?? "");
  const [salvasEm, setSalvasEm] = useState<Date | null>(null);

  function mudar(valor: string) {
    setTexto(valor);
    localStorage.setItem(chave, valor);
    setSalvasEm(new Date());
  }

  return (
    <aside id="anotacoes" aria-label="Anotações" className="fixed inset-0 z-40 flex flex-col bg-bg md:static md:z-auto md:w-[380px] md:flex-none md:border-l md:border-line">
      <div className="flex items-center justify-between h-14 md:h-[45px] shrink-0 pl-4 pr-2 border-b border-line text-[14px] leading-5 font-semibold">
        <span className="inline-flex items-center gap-2">
          <NotebookPen size={16} strokeWidth={1.5} aria-hidden />
          Anotações
        </span>
        <button type="button" className={ICONE} aria-label="Fechar anotações" title="Fechar anotações" onClick={onFechar}>
          <X size={16} strokeWidth={1.5} aria-hidden />
        </button>
      </div>
      <div className="flex-1 min-h-0 flex flex-col p-5">
        <label htmlFor="notas" className="sr-only">Anotações da consulta</label>
        <textarea
          id="notas"
          value={texto}
          onChange={(e) => mudar(e.target.value)}
          placeholder="Ex.: pula o café da manhã quando acorda atrasado"
          className="flex-1 min-h-60 resize-none px-3 py-2 border border-line-strong rounded-md bg-surface text-fg text-[16px] md:text-[15px] leading-6 placeholder:text-fg-muted focus-visible:outline-offset-0 focus-visible:border-transparent"
        />
      </div>
      <p className="m-0 px-4 py-2 border-t border-line text-[12px] leading-4 text-fg-muted">
        {salvasEm ? `Salvas neste navegador às ${hora(salvasEm)}` : "Ficam salvas só neste navegador"}
      </p>
    </aside>
  );
}
