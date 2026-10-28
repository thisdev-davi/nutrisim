import { ChevronDown } from "lucide-react";

const ETAPAS = ["Caso", "Anamnese", "Plano alimentar", "Cenários", "Retorno e feedback"];

function Ponto({ n, atual }: { n: number; atual: number }) {
  const cor = n === atual ? "border-transparent bg-accent text-on-accent" : n < atual ? "border-line-strong text-fg" : "border-line";
  return <span className={`grid place-items-center size-6 shrink-0 rounded-full border font-mono text-[12px] font-medium leading-none ${cor}`}>{n}</span>;
}

// desktop mostra a trilha inteira; o celular recolhe num details
export function Etapas({ atual, compacta = false }: { atual: number; compacta?: boolean }) {
  const lista = (vertical: boolean) => (
    <ol className={`flex m-0 p-0 list-none ${vertical ? "flex-col px-4 pb-2" : "items-center gap-2"}`}>
      {ETAPAS.map((etapa, i) => (
        <li key={etapa} aria-current={i + 1 === atual ? "step" : undefined} className="flex items-center gap-2">
          {!vertical && i > 0 && <span aria-hidden className="w-6 h-px bg-line-strong" />}
          <span className={`inline-flex items-center gap-2 text-[13px] leading-5 font-medium whitespace-nowrap ${vertical ? "min-h-11" : ""} ${i + 1 === atual ? "text-fg" : "text-fg-muted"}`}>
            <Ponto n={i + 1} atual={atual} />
            {etapa}
          </span>
        </li>
      ))}
    </ol>
  );

  if (!compacta) return <nav aria-label="Etapas da sessão" className="hidden md:block">{lista(false)}</nav>;

  return (
    <details className="group md:hidden border-b border-line">
      <summary className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-3 gap-y-2 min-h-11 px-4 py-3 list-none cursor-pointer text-fg-muted text-[14px] leading-5 [&::-webkit-details-marker]:hidden">
        <span>Etapa {atual} de {ETAPAS.length} · {ETAPAS[atual - 1]}</span>
        <ChevronDown size={16} strokeWidth={1.5} aria-hidden className="group-open:rotate-180" />
        <span aria-hidden className="col-span-full grid grid-cols-5 gap-1">
          {ETAPAS.map((etapa, i) => (
            <span key={etapa} className={`h-1 rounded-full ${i + 1 === atual ? "bg-accent" : i + 1 < atual ? "bg-line-strong" : "bg-surface-raised"}`} />
          ))}
        </span>
      </summary>
      <nav aria-label="Etapas da sessão">{lista(true)}</nav>
    </details>
  );
}
