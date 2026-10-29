"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ChevronRight, Plus } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { Alert } from "@/components/ui/Alert";
import { Avatar } from "@/components/ui/Avatar";
import { estiloBotao } from "@/components/ui/Button";
import { ETAPAS, Progresso } from "@/components/ui/Etapas";
import { DIFICULDADE, type Sessao } from "./sessoes/[id]/_anamnese/AnamneseChat";

interface Resumo extends Pick<Sessao, "id" | "etapa" | "dificuldade" | "paciente"> {
  perfil: string;
  criada_em: string;
}

const NUMERO_ETAPA: Record<string, number> = { anamnese: 2, plano: 3 };
const TITULO_SECAO = "m-0 text-[13px] leading-5 font-medium text-fg-muted";

const data = (iso: string) => new Date(iso).toLocaleDateString("pt-BR", { day: "numeric", month: "short" }).replace(" de ", " ").replace(".", "");

export default function InicioPage() {
  const { usuario } = useAuth();
  const { data: sessoes, isPending, error, refetch } = useQuery({ queryKey: ["sessoes"], queryFn: () => api<Resumo[]>("/sessoes") });

  // ponytail: nenhuma sessao conclui antes da etapa 5, entao a mais nova e a que continua
  const [atual, ...recentes] = sessoes ?? [];
  const etapa = atual && (NUMERO_ETAPA[atual.etapa] ?? 1);
  const nome = usuario?.nome.split(" ")[0];

  return (
    // my-auto: tela curta centraliza na vertical; se nao couber, comeca no topo
    <div className="w-full max-w-[960px] mx-auto md:my-auto px-4 pt-6 pb-8 md:px-10 md:pt-10 md:pb-16 flex flex-col gap-8 md:gap-10">
      <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
        <h1 className="flex-[1_1_420px] m-0 font-display font-medium text-[24px] leading-[30px] md:text-[28px] md:leading-[34px] tracking-[-0.02em] text-balance">
          Olá{nome && `, ${nome}`}.{" "}
          {!isPending && <span className="text-fg-muted">{atual ? `Retome ${atual.paciente.nome} ou comece um paciente novo.` : "Comece seu primeiro paciente."}</span>}
        </h1>
        <Link href="/caso/novo" className={`${estiloBotao(atual || isPending ? "secondary" : "primary")} w-full md:w-auto`}>
          <Plus size={16} strokeWidth={1.5} aria-hidden />
          Nova sessão
        </Link>
      </div>

      {isPending ? (
        <div aria-busy="true" aria-label="Carregando as sessões" className="h-[104px] rounded-lg bg-surface-raised" />
      ) : error ? (
        <Alert type="danger" action={<button type="button" onClick={() => refetch()} className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>}>
          Não foi possível carregar suas sessões. Verifique a conexão.
        </Alert>
      ) : (
        atual && (
          <section aria-labelledby="continuar" className="flex flex-col gap-4">
            <h2 id="continuar" className={TITULO_SECAO}>Continuar de onde parou</h2>
            <div className="flex flex-col md:flex-row md:flex-wrap md:items-center gap-6 p-6 border border-line rounded-lg bg-surface">
              <div className="flex flex-[1_1_200px] items-center gap-3 min-w-0">
                <Avatar nome={atual.paciente.nome} grande />
                <div className="flex flex-col gap-0.5 min-w-0">
                  <h3 className="m-0 text-[16px] leading-6 font-semibold">{atual.paciente.nome}, {atual.paciente.idade} anos</h3>
                  <span className="text-fg-muted text-[14px] leading-5">{atual.perfil} · Dificuldade {DIFICULDADE[atual.dificuldade]}</span>
                </div>
              </div>
              <div className="flex flex-[0_1_200px] flex-col gap-2">
                <span className="text-fg-muted text-[14px] leading-5">Etapa {etapa} de {ETAPAS.length} · {ETAPAS[etapa - 1]}</span>
                <Progresso atual={etapa} />
              </div>
              <Link href={`/sessoes/${atual.id}`} className={estiloBotao("primary")}>Continuar sessão</Link>
            </div>
          </section>
        )
      )}

      {recentes.length > 0 && (
        <section aria-labelledby="recentes" className="flex flex-col gap-4">
          <h2 id="recentes" className={TITULO_SECAO}>Sessões recentes</h2>
          <ul className="m-0 p-0 list-none border border-line rounded-lg overflow-hidden divide-y divide-line">
            {recentes.map((s) => (
              <li key={s.id}>
                {/* ponytail: abre a sessao; vira "Ver feedback" quando a etapa 5 existir */}
                <Link href={`/sessoes/${s.id}`} className="group flex items-center gap-4 min-h-11 py-3 pl-5 pr-4 transition-colors hover:bg-surface-hover">
                  <span className="flex flex-1 flex-col min-w-0">
                    <span className="text-[14px] leading-5 font-medium">{s.paciente.nome}, {s.paciente.idade} anos</span>
                    <span className="text-fg-muted text-[13px] leading-5 truncate">{s.perfil} · {DIFICULDADE[s.dificuldade]}</span>
                  </span>
                  <span className="text-fg-muted font-mono text-[12px] leading-5 whitespace-nowrap">{data(s.criada_em)}</span>
                  <span className="hidden md:inline-flex items-center gap-1 text-fg-muted text-[13px] leading-5 font-medium whitespace-nowrap group-hover:text-fg">
                    Abrir
                    <ChevronRight size={16} strokeWidth={1.5} aria-hidden />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
