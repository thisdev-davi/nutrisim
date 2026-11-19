"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface Alimento {
  id: number;
  nome: string;
  kcal: number | null;
}

// autocompletar da TACO no padrao combobox: setas escolhem, enter adiciona, esc fecha
export function BuscaAlimento({ id, rotulo, onEscolher }: { id: string; rotulo: string; onEscolher: (a: Alimento) => void }) {
  const [termo, setTermo] = useState("");
  const [busca, setBusca] = useState("");
  const [ativo, setAtivo] = useState(0);
  const [aberto, setAberto] = useState(false);

  // espera a digitacao parar para nao buscar a cada letra
  useEffect(() => {
    const t = setTimeout(() => setBusca(termo.trim()), 300);
    return () => clearTimeout(t);
  }, [termo]);

  const { data: opcoes = [], isFetching } = useQuery({
    queryKey: ["alimentos", busca],
    queryFn: () => api<Alimento[]>(`/alimentos?nome=${encodeURIComponent(busca)}`),
    enabled: busca.length >= 2,
    staleTime: Infinity, // a TACO nao muda
  });
  const mostrar = aberto && busca.length >= 2 && busca === termo.trim();

  function escolher(a: Alimento | undefined) {
    if (!a) return;
    onEscolher(a);
    setTermo("");
    setAberto(false);
  }

  return (
    <div className="relative">
      <label htmlFor={id} className="sr-only">{rotulo}</label>
      <input
        id={id}
        role="combobox"
        aria-expanded={mostrar}
        aria-controls={`${id}-lista`}
        aria-autocomplete="list"
        aria-activedescendant={mostrar && opcoes[ativo] ? `${id}-${ativo}` : undefined}
        value={termo}
        maxLength={100}
        placeholder="Buscar alimento na TACO…"
        onChange={(e) => {
          setTermo(e.target.value);
          setAtivo(0);
          setAberto(true);
        }}
        onBlur={() => setAberto(false)}
        onKeyDown={(e) => {
          if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            e.preventDefault();
            setAberto(true);
            const passo = e.key === "ArrowDown" ? 1 : -1;
            setAtivo((i) => (opcoes.length ? (i + passo + opcoes.length) % opcoes.length : 0));
          } else if (e.key === "Enter" && mostrar) {
            e.preventDefault();
            escolher(opcoes[ativo]);
          } else if (e.key === "Escape") setAberto(false);
        }}
        className="w-full h-11 md:h-9 px-3 border border-line-strong rounded-md bg-surface text-fg text-[16px] md:text-[15px] leading-6 placeholder:text-fg-muted hover:border-fg-muted focus-visible:outline-offset-0 focus-visible:border-transparent"
      />
      {mostrar && (
        <ul id={`${id}-lista`} role="listbox" aria-label={rotulo} className="absolute z-10 left-0 right-0 mt-1 max-h-64 overflow-y-auto m-0 p-1 list-none border border-line rounded-md bg-surface shadow-[var(--overlay)]">
          {opcoes.map((a, i) => (
            <li
              key={a.id}
              id={`${id}-${i}`}
              role="option"
              aria-selected={i === ativo}
              // mousedown antes do blur do campo, senao a lista some antes do clique
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => escolher(a)}
              className={`flex justify-between gap-3 px-3 py-2 rounded-[4px] cursor-pointer text-[14px] leading-5 ${i === ativo ? "bg-surface-raised" : ""}`}
            >
              <span className="min-w-0 [overflow-wrap:anywhere]">{a.nome}</span>
              {a.kcal !== null && <span className="shrink-0 font-mono text-[12px] text-fg-muted">{Math.round(a.kcal)} kcal/100 g</span>}
            </li>
          ))}
          {!opcoes.length && <li className="px-3 py-2 text-[14px] text-fg-muted">{isFetching ? "Buscando…" : "Nenhum alimento encontrado"}</li>}
        </ul>
      )}
    </div>
  );
}
