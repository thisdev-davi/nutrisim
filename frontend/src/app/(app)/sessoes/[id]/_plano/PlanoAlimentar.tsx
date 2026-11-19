"use client";

import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, TriangleAlert, X } from "lucide-react";
import { api, type Erro } from "@/lib/api";
import { estiloBotao } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { Etapas } from "@/components/ui/Etapas";
import { chaveSessao, type Etapa, type Sessao } from "../_anamnese/AnamneseChat";
import { BuscaAlimento } from "./BuscaAlimento";

interface Violacao {
  tipo: string;
  mensagem: string;
  refeicao: string | null;
  alimento_id: number | null;
}

interface Plano {
  refeicoes: { nome: string; itens: { alimento_id: number; gramas: number; nome: string; kcal: number }[]; composicao: { valores: Record<string, number> } }[];
  total: { valores: Record<string, number> };
  get_kcal: number;
  adequacao: Record<string, { consumo: number; referencia: number; percentual: number; classificacao: "abaixo" | "adequado" | "acima" }>;
  violacoes: Violacao[];
  custo_diario_reais: number;
  sem_preco: string[];
}

type Refeicao = { nome: string; itens: { alimento_id: number; nome: string; gramas: number }[] };

// ponytail: refeicoes fixas, sem renomear nem criar; adicionar quando o caso pedir
const PADRAO = ["Café da manhã", "Lanche da manhã", "Almoço", "Lanche da tarde", "Jantar", "Ceia"];

const NUTRIENTES: [string, string, string][] = [
  ["proteina", "Proteína", "g"],
  ["carboidratos", "Carboidratos", "g"],
  ["lipidios", "Lipídios", "g"],
  ["gordura_saturada", "Gordura saturada", "g"],
  ["fibra_alimentar", "Fibra", "g"],
  ["sodio", "Sódio", "mg"],
  ["potassio", "Potássio", "mg"],
  ["calcio", "Cálcio", "mg"],
  ["ferro", "Ferro", "mg"],
  ["vitamina_c", "Vitamina C", "mg"],
];

const CLASSE = { abaixo: "text-warning", adequado: "text-success", acima: "text-danger" };

const num = (n: number, casas = 0) => n.toLocaleString("pt-BR", { maximumFractionDigits: casas });
const valida = (g: number) => g > 0 && g <= 2000; // limite do ItemPlano
const chavePlano = (id: string) => ["plano", id];

function Aviso({ v }: { v: Violacao }) {
  return (
    <p className="m-0 flex gap-1 text-[13px] leading-5 text-warning">
      <TriangleAlert size={16} strokeWidth={1.5} aria-hidden className="shrink-0 mt-0.5" />
      {v.mensagem}
    </p>
  );
}

// encerrar e encaminhar so trocam a etapa no cache; a pagina troca de tela sozinha
function useAvancar(sessaoId: string, acao: "encerrar" | "encaminhar") {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (corpo?: { motivo: string }) => api<{ etapa: Etapa }>(`/sessoes/${sessaoId}/plano/${acao}`, { method: "POST", body: corpo && JSON.stringify(corpo) }),
    onSuccess: ({ etapa }) => {
      queryClient.setQueryData<Sessao>(chaveSessao(sessaoId), (s) => s && { ...s, etapa });
      queryClient.invalidateQueries({ queryKey: ["sessoes"] });
    },
    // outra aba ja mudou a etapa: recarrega a sessao e vai para a tela certa
    onError: (e: Erro) => e.codigo === "etapa_invalida" && queryClient.invalidateQueries({ queryKey: chaveSessao(sessaoId) }),
  });
}

export function PlanoAlimentar({ sessaoId }: { sessaoId: string }) {
  const { data, error, refetch } = useQuery({
    queryKey: chavePlano(sessaoId),
    // sem PUT ainda o GET da 404: tela vazia, sem erro
    queryFn: () => api<Plano>(`/sessoes/${sessaoId}/plano`).catch((e: Erro) => (e.codigo === "plano_nao_encontrado" ? null : Promise.reject(e))),
    retry: false,
    staleTime: Infinity, // so esta tela muda o plano, e o PUT ja atualiza o cache
  });

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <Etapas atual={3} compacta />
      <div className="px-4 py-2 md:px-8 md:py-4 border-b border-line">
        <Etapas atual={3} />
      </div>
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 md:px-8 md:py-8">
        {error ? (
          <div className="max-w-[720px] mx-auto">
            <Alert type="danger" action={<button type="button" onClick={() => refetch()} className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>}>
              {(error as unknown as Erro).mensagem ?? "Não foi possível carregar o plano."}
            </Alert>
          </div>
        ) : data === undefined ? (
          <div aria-busy="true" aria-label="Carregando o plano" className="max-w-[1080px] mx-auto flex flex-col gap-4">
            <div className="h-32 rounded-lg bg-surface-raised" />
            <div className="h-32 rounded-lg bg-surface-raised" />
          </div>
        ) : (
          <Editor sessaoId={sessaoId} calculado={data} />
        )}
      </div>
    </div>
  );
}

function Editor({ sessaoId, calculado }: { sessaoId: string; calculado: Plano | null }) {
  const queryClient = useQueryClient();
  const [refeicoes, setRefeicoes] = useState<Refeicao[]>(() =>
    calculado ? calculado.refeicoes.map((r) => ({ nome: r.nome, itens: r.itens.map(({ alimento_id, nome, gramas }) => ({ alimento_id, nome, gramas })) })) : PADRAO.map((nome) => ({ nome, itens: [] })),
  );
  const [sujo, setSujo] = useState(false); // ha mudanca que o backend ainda nao calculou
  const [falhou, setFalhou] = useState(false);
  const pedido = useRef(0);
  const encerrar = useAvancar(sessaoId, "encerrar");

  const invalida = refeicoes.some((r) => r.itens.some((i) => !valida(i.gramas)));

  function mudar(f: (r: Refeicao[]) => Refeicao[]) {
    setRefeicoes(f);
    setSujo(true);
  }

  // o PUT leva o plano inteiro; so a resposta do ultimo pedido redesenha a tela
  useEffect(() => {
    if (!sujo || invalida) return;
    const n = ++pedido.current;
    const t = setTimeout(async () => {
      const corpo = { refeicoes: refeicoes.map((r) => ({ nome: r.nome, itens: r.itens.map(({ alimento_id, gramas }) => ({ alimento_id, gramas })) })) };
      try {
        const plano = await api<Plano>(`/sessoes/${sessaoId}/plano`, { method: "PUT", body: JSON.stringify(corpo) });
        if (n !== pedido.current) return;
        queryClient.setQueryData(chavePlano(sessaoId), plano);
        setSujo(false);
        setFalhou(false);
      } catch (e) {
        if (n !== pedido.current) return;
        if ((e as Erro).codigo === "etapa_invalida") queryClient.invalidateQueries({ queryKey: chaveSessao(sessaoId) });
        else setFalhou(true);
      }
    }, 400);
    return () => clearTimeout(t);
  }, [refeicoes, sujo, invalida, sessaoId, queryClient]);

  const doDia = calculado?.violacoes.filter((v) => v.refeicao === null && v.alimento_id === null) ?? [];
  const temItens = refeicoes.some((r) => r.itens.length);
  const kcal = calculado?.total.valores.kcal ?? 0;

  return (
    <div className="max-w-[1080px] mx-auto grid gap-6 md:grid-cols-[minmax(0,1fr)_320px] md:items-start">
      <div className="flex flex-col gap-4 min-w-0">
        <h1 className="m-0 text-[18px] leading-[26px] font-semibold">Monte o plano alimentar</h1>
        {refeicoes.map((r, ri) => {
          const calc = calculado?.refeicoes.find((c) => c.nome === r.nome);
          const daRefeicao = calculado?.violacoes.filter((v) => v.refeicao === r.nome && v.alimento_id === null) ?? [];
          const idTitulo = `refeicao-${ri}`;
          return (
            <section key={r.nome} aria-labelledby={idTitulo} className="flex flex-col gap-3 p-4 border border-line rounded-lg">
              <div className="flex items-baseline justify-between gap-3">
                <h2 id={idTitulo} className="m-0 text-[15px] leading-[22px] font-semibold">{r.nome}</h2>
                {calc && r.itens.length > 0 && <span className="font-mono text-[12px] text-fg-muted">{num(calc.composicao.valores.kcal)} kcal</span>}
              </div>
              {daRefeicao.map((v, i) => <Aviso key={i} v={v} />)}
              {r.itens.length > 0 && (
                <ul className="m-0 p-0 list-none flex flex-col gap-2">
                  {r.itens.map((item, ii) => {
                    const idGramas = `gramas-${ri}-${ii}`;
                    const doItem = calculado?.violacoes.filter((v) => v.refeicao === r.nome && v.alimento_id === item.alimento_id) ?? [];
                    const kcalItem = calc?.itens.find((c) => c.alimento_id === item.alimento_id)?.kcal;
                    const trocar = (f: (itens: Refeicao["itens"]) => Refeicao["itens"]) => mudar((rs) => rs.map((x, k) => (k === ri ? { ...x, itens: f(x.itens) } : x)));
                    return (
                      <li key={`${item.alimento_id}-${ii}`} className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <span className="flex-1 min-w-0 text-[14px] leading-5 [overflow-wrap:anywhere]">{item.nome}</span>
                          <label htmlFor={idGramas} className="sr-only">Gramas de {item.nome}</label>
                          <input
                            id={idGramas}
                            type="number"
                            inputMode="decimal"
                            min={1}
                            max={2000}
                            value={item.gramas || ""}
                            aria-invalid={!valida(item.gramas)}
                            onChange={(e) => trocar((itens) => itens.map((x, k) => (k === ii ? { ...x, gramas: Number(e.target.value) } : x)))}
                            className={`w-20 h-11 md:h-8 px-2 border rounded-md bg-surface text-fg text-right text-[16px] md:text-[14px] focus-visible:outline-offset-0 ${valida(item.gramas) ? "border-line-strong" : "border-danger"}`}
                          />
                          <span className="text-[13px] text-fg-muted">g</span>
                          <span className="hidden sm:block w-16 text-right font-mono text-[12px] text-fg-muted">{kcalItem !== undefined && `${num(kcalItem)} kcal`}</span>
                          <button type="button" aria-label={`Remover ${item.nome} de ${r.nome}`} onClick={() => trocar((itens) => itens.filter((_, k) => k !== ii))} className="grid place-items-center size-11 md:size-8 rounded-md text-fg-muted hover:bg-surface-raised hover:text-fg cursor-pointer">
                            <X size={16} strokeWidth={1.5} aria-hidden />
                          </button>
                        </div>
                        {doItem.map((v, i) => <Aviso key={i} v={v} />)}
                      </li>
                    );
                  })}
                </ul>
              )}
              <BuscaAlimento
                id={`busca-${ri}`}
                rotulo={`Adicionar alimento em ${r.nome}`}
                onEscolher={(a) => mudar((rs) => rs.map((x, k) => (k === ri ? { ...x, itens: [...x.itens, { alimento_id: a.id, nome: a.nome, gramas: 100 }] } : x)))}
              />
            </section>
          );
        })}
      </div>

      <aside aria-label="Totais do dia" className="flex flex-col gap-4 p-4 border border-line rounded-lg md:sticky md:top-0">
        <div aria-live="polite" className="flex flex-col gap-2">
          <p className="m-0 text-[13px] leading-5 text-fg-muted">{invalida ? "Porção entre 1 e 2.000 g para salvar" : sujo ? "Calculando…" : calculado ? "Salvo" : "Adicione alimentos para ver os totais"}</p>
          {calculado && (
            <>
              <p className="m-0 text-[15px] leading-[22px] font-semibold">
                {num(kcal)} de {num(calculado.get_kcal)} kcal do GET ({num((kcal / calculado.get_kcal) * 100)}%)
              </p>
              <p className="m-0 text-[13px] leading-5">
                Custo: R$ {calculado.custo_diario_reais.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}/dia
                {calculado.sem_preco.length > 0 && <span className="block text-fg-muted">Incompleto: sem preço para {calculado.sem_preco.join(", ")}.</span>}
              </p>
              {doDia.map((v, i) => <Alert key={i} type="warning">{v.mensagem}</Alert>)}
              {calculado.violacoes.length > doDia.length && <p className="sr-only">{calculado.violacoes.length - doDia.length} alertas junto das refeições</p>}
            </>
          )}
          {falhou && <Alert type="danger" action={<button type="button" onClick={() => mudar((r) => [...r])} className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>}>Não foi possível salvar o plano.</Alert>}
        </div>
        {calculado && (
          <dl className="m-0 grid grid-cols-[1fr_auto] gap-x-3 gap-y-1 text-[13px] leading-5">
            {NUTRIENTES.map(([chave, nome, unidade]) => {
              const a = calculado.adequacao[chave];
              return [
                <dt key={`${chave}-n`} className="text-fg-muted">{nome}</dt>,
                <dd key={`${chave}-v`} className="m-0 text-right font-mono text-[12px]">
                  {a ? (
                    <>
                      {num(a.consumo, 1)}/{num(a.referencia)} {unidade} <span className={CLASSE[a.classificacao]}>{num(a.percentual)}% {a.classificacao}</span>
                    </>
                  ) : (
                    `${num(calculado.total.valores[chave] ?? 0, 1)} ${unidade}`
                  )}
                </dd>,
              ];
            })}
          </dl>
        )}
        <div className="flex flex-col gap-2 pt-2 border-t border-line">
          {encerrar.error && encerrar.error.codigo !== "etapa_invalida" && <Alert type="danger">{encerrar.error.mensagem}</Alert>}
          <button type="button" className={estiloBotao("primary", true)} disabled={!calculado || !temItens || sujo || encerrar.isPending} onClick={() => encerrar.mutate(undefined)}>
            Encerrar o plano e ver cenários
            <ArrowRight size={16} strokeWidth={1.5} aria-hidden />
          </button>
          <Encaminhar sessaoId={sessaoId} />
        </div>
      </aside>
    </div>
  );
}

// ADR-006: em todo perfil o estudante pode encaminhar no lugar do plano
function Encaminhar({ sessaoId }: { sessaoId: string }) {
  const dialogo = useRef<HTMLDialogElement>(null);
  const [motivo, setMotivo] = useState("");
  const { mutate, isPending, error } = useAvancar(sessaoId, "encaminhar");

  return (
    <>
      <button type="button" className={estiloBotao("secondary", true)} onClick={() => dialogo.current?.showModal()}>
        Encaminhar o paciente
      </button>
      <dialog ref={dialogo} aria-labelledby="encaminhar-titulo" className="m-auto w-[calc(100%-32px)] max-w-[440px] p-6 border border-line rounded-lg bg-surface text-fg shadow-[var(--overlay)] backdrop:bg-black/60">
        <form
          className="flex flex-col gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            mutate({ motivo: motivo.trim() });
          }}
        >
          <h2 id="encaminhar-titulo" className="m-0 text-[18px] leading-[26px] font-semibold tracking-[-0.02em]">Encaminhar o paciente?</h2>
          <p className="m-0 text-fg-muted">A sessão vai direto para o retorno, sem cenários. Um plano já salvo fica guardado, mas não é avaliado.</p>
          <label htmlFor="motivo" className="text-[13px] leading-4 font-medium">Motivo do encaminhamento</label>
          <textarea
            id="motivo"
            rows={4}
            maxLength={2000}
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            className="px-3 py-2 border border-line-strong rounded-md bg-surface text-fg text-[16px] md:text-[15px] leading-6 resize-y focus-visible:outline-offset-0 focus-visible:border-transparent"
          />
          <span className="self-end font-mono text-[12px] text-fg-muted">{motivo.length}/2000</span>
          {error && error.codigo !== "etapa_invalida" && <Alert type="danger">{error.mensagem}</Alert>}
          <div className="flex flex-wrap justify-end gap-2 pt-3">
            <button type="button" className={estiloBotao("secondary", true)} onClick={() => dialogo.current?.close()}>
              Voltar ao plano
            </button>
            <button type="submit" className={estiloBotao("primary", true)} disabled={!motivo.trim() || isPending}>
              Encaminhar
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
