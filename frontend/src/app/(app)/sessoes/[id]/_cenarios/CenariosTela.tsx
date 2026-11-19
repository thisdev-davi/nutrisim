"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type Erro } from "@/lib/api";
import { Alert } from "@/components/ui/Alert";
import { Etapas } from "@/components/ui/Etapas";

interface Adequacao {
  percentual: number;
  classificacao: "abaixo" | "adequado" | "acima";
}

interface Cenario {
  peso: { semana: number; peso_kg: number }[];
  adequacao: Record<string, Adequacao>;
}

export interface Cenarios {
  ideal: Cenario;
  realista: Cenario & {
    adesao: { refeicao: string; adesao: number }[];
    substituicoes: { refeicao: string; original_id: number; original: string; substituto_id: number; substituto: string; motivo: string }[];
  };
  aviso: string;
}

const NUTRIENTE: Record<string, string> = {
  kcal: "Energia",
  proteina: "Proteína",
  carboidratos: "Carboidratos",
  lipidios: "Lipídios",
  fibra_alimentar: "Fibras",
  sodio: "Sódio",
  calcio: "Cálcio",
  ferro: "Ferro",
  potassio: "Potássio",
  vitamina_c: "Vitamina C",
  gordura_saturada: "Gordura saturada",
};

const kg = (n: number) => n.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
const pct = (n: number) => `${Math.round(n)}%`;
const SECAO = "flex flex-col gap-3 p-5 border border-line rounded-lg";
const TITULO = "m-0 text-[15px] leading-[22px] font-semibold";

// svg na mao: o projeto nao tem lib de graficos e duas linhas nao justificam uma
function GraficoPeso({ ideal, realista }: { ideal: Cenario["peso"]; realista: Cenario["peso"] }) {
  const [L, T, W, H] = [36, 8, 312, 148]; // area do plot dentro do viewBox 320x180
  const pesos = [...ideal, ...realista].map((p) => p.peso_kg);
  const min = Math.floor(Math.min(...pesos) - 0.5);
  const max = Math.ceil(Math.max(...pesos) + 0.5);
  const semanas = Math.max(...ideal.map((p) => p.semana), 1);
  const x = (s: number) => L + ((W - L) * s) / semanas;
  const y = (p: number) => H - ((H - T) * (p - min)) / (max - min);
  const linha = (serie: Cenario["peso"]) => serie.map((p) => `${x(p.semana)},${y(p.peso_kg)}`).join(" ");

  return (
    <figure className="m-0 flex flex-col gap-2">
      <svg viewBox="0 0 320 180" aria-hidden className="w-full max-w-[480px] text-fg-muted text-[11px]">
        {[min, (min + max) / 2, max].map((v) => (
          <g key={v}>
            <line x1={L} x2={W} y1={y(v)} y2={y(v)} stroke="var(--line)" />
            <text x={L - 4} y={y(v) + 4} textAnchor="end" fill="currentColor">{kg(v)}</text>
          </g>
        ))}
        {ideal.map((p) => (
          <text key={p.semana} x={x(p.semana)} y={H + 14} textAnchor="middle" fill="currentColor">{p.semana}</text>
        ))}
        <text x={(L + W) / 2} y={178} textAnchor="middle" fill="currentColor">semana</text>
        <polyline points={linha(ideal)} fill="none" stroke="var(--accent)" strokeWidth={2} />
        {/* tracejado: a serie se distingue sem depender da cor */}
        <polyline points={linha(realista)} fill="none" stroke="var(--fg-secondary)" strokeWidth={2} strokeDasharray="5 4" />
      </svg>
      <figcaption className="flex gap-4 text-[13px] leading-5 text-fg-muted">
        <span className="inline-flex items-center gap-2"><span aria-hidden className="w-4 h-0.5 bg-accent" />Ideal</span>
        <span className="inline-flex items-center gap-2"><span aria-hidden className="w-4 border-t-2 border-dashed border-fg-secondary" />Realista</span>
      </figcaption>
      <table className="sr-only">
        <caption>Peso projetado por semana, em kg</caption>
        <thead><tr><th>Semana</th><th>Ideal</th><th>Realista</th></tr></thead>
        <tbody>
          {ideal.map((p, i) => (
            <tr key={p.semana}><td>{p.semana}</td><td>{kg(p.peso_kg)}</td><td>{realista[i] && kg(realista[i].peso_kg)}</td></tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}

// a trilha vai ate 200%; o traco no meio marca os 100% da DRI
function Barra({ nome, a }: { nome: string; a?: Adequacao }) {
  if (!a) return null;
  return (
    <div className="grid grid-cols-[64px_1fr_auto] items-center gap-2 text-[13px] leading-5">
      <span className="text-fg-muted">{nome}</span>
      <span aria-hidden className="relative h-2 rounded-full bg-surface-raised overflow-hidden">
        <span className={`absolute inset-y-0 left-0 rounded-full ${a.classificacao === "adequado" ? "bg-success" : "bg-warning"}`} style={{ width: `${Math.min(a.percentual, 200) / 2}%` }} />
        <span className="absolute inset-y-0 left-1/2 w-px bg-fg" />
      </span>
      <span className="font-mono">{pct(a.percentual)} · {a.classificacao}</span>
    </div>
  );
}

export function CenariosTela({ sessaoId }: { sessaoId: string }) {
  // post idempotente: gera na primeira chamada e repete o resultado depois
  const { data, error, refetch, isFetching } = useQuery({
    queryKey: ["cenarios", sessaoId],
    queryFn: () => api<Cenarios>(`/sessoes/${sessaoId}/cenarios`, { method: "POST" }),
    retry: false,
    staleTime: Infinity,
  });
  const { ideal, realista } = data ?? {};
  // a troca pode citar refeicao sem adesao estimada; junta as duas listas
  const refeicoes = realista ? [...new Set([...realista.adesao, ...realista.substituicoes].map((x) => x.refeicao))] : [];

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <Etapas atual={4} compacta />
      <div className="px-4 py-2 md:px-8 md:py-4 border-b border-line">
        <Etapas atual={4} />
      </div>
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 md:px-6 md:py-8">
        <div className="w-full max-w-[720px] mx-auto flex flex-col gap-6">
          <h1 className="m-0 text-[18px] leading-[26px] font-semibold">Cenários do plano</h1>
          {error && !isFetching ? (
            <Alert type="danger" action={<button type="button" onClick={() => refetch()} className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>}>
              {(error as unknown as Erro).mensagem ?? "Não foi possível gerar os cenários."}
            </Alert>
          ) : !data || !ideal || !realista ? (
            <div aria-busy="true" className="flex flex-col gap-4">
              <p className="m-0 text-fg-muted">Gerando os cenários. Isso leva alguns segundos…</p>
              <div className="h-[220px] rounded-lg bg-surface-raised" />
              <div className="h-[160px] rounded-lg bg-surface-raised" />
            </div>
          ) : (
            <>
              <Alert type="warning" title="Limitação da projeção">{data.aviso}</Alert>

              <section className={SECAO}>
                <h2 className={TITULO}>Peso projetado (kg)</h2>
                <GraficoPeso ideal={ideal.peso} realista={realista.peso} />
              </section>

              <section className={SECAO}>
                <h2 className={TITULO}>Adequação à DRI</h2>
                <p className="m-0 text-[13px] leading-5 text-fg-muted">O traço marca 100% da referência.</p>
                <ul className="m-0 p-0 list-none flex flex-col gap-4">
                  {Object.entries(ideal.adequacao).map(([chave, a]) => (
                    <li key={chave} className="flex flex-col gap-1">
                      <span className="text-[14px] font-medium">{NUTRIENTE[chave] ?? chave}</span>
                      <Barra nome="Ideal" a={a} />
                      <Barra nome="Realista" a={realista.adequacao[chave]} />
                    </li>
                  ))}
                </ul>
              </section>

              <section className={SECAO}>
                <h2 className={TITULO}>Cenário realista por refeição</h2>
                {refeicoes.map((r) => {
                  const adesao = realista.adesao.find((a) => a.refeicao === r);
                  const trocas = realista.substituicoes.filter((s) => s.refeicao === r);
                  return (
                    <div key={r} className="flex flex-col gap-1 pt-3 border-t border-line first-of-type:border-0 first-of-type:pt-0">
                      <h3 className="m-0 flex justify-between gap-2 text-[14px] leading-5 font-medium">
                        {r}
                        {adesao && <span className="font-mono text-fg-muted">adesão {pct(adesao.adesao * 100)}</span>}
                      </h3>
                      {trocas.length ? (
                        <ul className="m-0 pl-4 flex flex-col gap-1 text-[13px] leading-5">
                          {trocas.map((s) => (
                            <li key={`${s.original_id}-${s.substituto_id}`}>
                              {s.original} <span aria-hidden>→</span><span className="sr-only">trocado por</span> {s.substituto}
                              <span className="text-fg-muted"> · {s.motivo}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="m-0 text-[13px] leading-5 text-fg-muted">Sem substituições.</p>
                      )}
                    </div>
                  );
                })}
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
