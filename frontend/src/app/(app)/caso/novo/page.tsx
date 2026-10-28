"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { LoaderCircle, Sparkle } from "lucide-react";
import { env } from "@/lib/env";

import { Select } from "@/components/ui/Select";
import { Button, estiloBotao } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { Etapas } from "@/components/ui/Etapas";

interface Perfil { id: string; nome: string; descricao: string; }
type Dificuldade = "facil" | "medio" | "dificil";
interface Opcoes { perfis: Perfil[]; dificuldades: Dificuldade[]; }
interface NovaSessao { perfil_id: string; dificuldade: Dificuldade; }
interface Sessao { id: string; }

const DIFICULDADES: Record<Dificuldade, { rotulo: string; texto: string }> = {
  facil: { rotulo: "Fácil", texto: "Colaborativo: conta a rotina com detalhes e quase não esconde nada." },
  medio: { rotulo: "Média", texto: "Ambivalente: responde curto, subestima porções e esconde alguns hábitos." },
  dificil: { rotulo: "Difícil", texto: "Resistente: respostas vagas, esquece itens e só revela hábitos com as perguntas certas." },
};

const CONTEUDO_FICHA = ["História de vida", "Rotina de trabalho", "Limitações financeiras", "Resistências alimentares"];

export default function NovoCasoPage() {
  const router = useRouter();
  const alertaErro = useRef<HTMLDivElement>(null);

  const [perfilId, setPerfilId] = useState("");
  const [dificuldade, setDificuldade] = useState<Dificuldade>("medio");

  const { data: opcoes, isPending: carregandoOpcoes, error: erroCarregar, refetch: recarregarOpcoes } = useQuery({
    queryKey: ["perfis-e-dificuldades"],
    queryFn: async (): Promise<Opcoes> => {
      const resp = await fetch(`${env.api.url}/api/perfis`);
      if (!resp.ok) throw new Error("Não foi possível carregar os perfis disponíveis.");
      return resp.json();
    },
  });

  const { mutate: gerarCaso, isPending: gerandoCaso, error: erroCriar } = useMutation({
    mutationFn: async (dados: NovaSessao): Promise<Sessao> => {
      const resp = await fetch(`${env.api.url}/api/sessoes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });
      if (!resp.ok) throw new Error("Falha ao criar o caso clínico.");
      return resp.json();
    },
    onSuccess: (sessao) => router.push(`/sessoes/${sessao.id}`),
  });

  // o erro da ia fica acima dos botoes e recebe o foco
  useEffect(() => {
    if (erroCriar) alertaErro.current?.focus();
  }, [erroCriar]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!perfilId || gerandoCaso) return;
    gerarCaso({ perfil_id: perfilId, dificuldade });
  }

  const perfilSelecionado = opcoes?.perfis.find((p) => p.id === perfilId);

  return (
    <>
      <Etapas atual={1} compacta />

      <div className="w-full max-w-[960px] mx-auto px-4 pt-6 md:px-10 md:pt-10 md:pb-16 md:my-auto flex flex-col gap-6 md:gap-8">
        <Etapas atual={1} />

        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="m-0 font-display font-medium text-[24px] leading-[30px] md:text-[28px] md:leading-[34px] tracking-[-0.02em] text-balance">
              Configurar novo paciente
            </h1>
            <span className="md:hidden inline-flex items-center gap-1.5 h-6 px-2.5 rounded-full bg-accent-soft text-accent text-[12px] font-medium">
              <Sparkle size={12} strokeWidth={1.5} aria-hidden />
              Gerado por IA
            </span>
          </div>
          <p className="m-0 max-w-[62ch] text-fg-muted">
            <span className="md:hidden">Escolha os parâmetros. A IA cria um paciente único para a anamnese.</span>
            <span className="hidden md:inline">Escolha os parâmetros da simulação. A IA cria um paciente único a partir deles, e você descobre os detalhes conversando com ele na anamnese.</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} aria-label="Parâmetros da simulação" className="flex flex-col gap-6 md:p-6 md:border md:border-line md:rounded-lg md:bg-surface">
          {carregandoOpcoes ? (
            <div className="grid md:grid-cols-2 gap-4" aria-busy="true" aria-label="Carregando os perfis">
              {[0, 1].map((i) => (
                <div key={i} className="flex flex-col gap-1.5">
                  <div className="w-1/2 h-4 rounded-md bg-surface-raised" />
                  <div className="h-11 rounded-md bg-surface-raised" />
                </div>
              ))}
            </div>
          ) : erroCarregar ? (
            <Alert
              type="danger"
              action={
                <button type="button" onClick={() => recarregarOpcoes()} className="text-[13px] font-medium underline cursor-pointer">
                  Tentar de novo
                </button>
              }
            >
              Não foi possível carregar os perfis. Verifique a conexão.
            </Alert>
          ) : (
            <>
              <fieldset disabled={gerandoCaso} className="m-0 p-0 border-0 min-w-0 flex flex-col gap-4 md:gap-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <Select
                    id="perfil"
                    label="Patologia ou objetivo"
                    value={perfilId}
                    onChange={(e) => setPerfilId(e.target.value)}
                    required
                    helpText={perfilSelecionado?.descricao ?? "O perfil define a condição de saúde do paciente."}
                  >
                    <option value="">Selecione…</option>
                    {opcoes?.perfis.map((p) => (
                      <option key={p.id} value={p.id}>{p.nome}</option>
                    ))}
                  </Select>
                </div>

                <fieldset className="m-0 p-0 border-0 min-w-0">
                  <legend className="mb-1.5 p-0 text-[13px] leading-4 font-medium">Dificuldade</legend>
                  <div className="grid md:grid-cols-3 gap-3">
                    {opcoes?.dificuldades.map((d) => (
                      <label
                        key={d}
                        className="relative flex flex-col gap-1 px-4 py-3.5 border border-line-strong rounded-lg cursor-pointer transition-colors hover:border-fg-muted has-checked:border-fg has-checked:bg-surface-raised has-checked:shadow-[inset_0_0_0_1px_var(--fg)] has-focus-visible:outline-2 has-focus-visible:outline-accent has-focus-visible:outline-offset-2"
                      >
                        <input type="radio" name="dificuldade" value={d} checked={dificuldade === d} onChange={() => setDificuldade(d)} className="absolute opacity-0 pointer-events-none" />
                        <span className="text-[14px] leading-5 font-medium">{DIFICULDADES[d].rotulo}</span>
                        <span className="text-[13px] leading-5 text-fg-muted">{DIFICULDADES[d].texto}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>
              </fieldset>

              <div className="flex flex-wrap items-center gap-2">
                <span className="basis-full text-[13px] leading-5 font-medium text-fg-muted">A ficha oculta tem</span>
                {CONTEUDO_FICHA.map((item) => (
                  <span key={item} className="inline-flex items-center h-6 px-2.5 rounded-full border border-line-strong text-fg-muted text-[12px] font-medium whitespace-nowrap">
                    {item}
                  </span>
                ))}
              </div>

              {erroCriar && (
                <div ref={alertaErro} tabIndex={-1} className="outline-none">
                  <Alert type="danger" action={<button type="submit" className="text-[13px] font-medium underline cursor-pointer">Tentar de novo</button>}>
                    A IA não conseguiu criar o paciente agora. Suas escolhas continuam marcadas.
                  </Alert>
                </div>
              )}

              {/* no celular vira a barra fixa no rodape */}
              <div className="sticky bottom-0 -mx-4 px-4 py-3 border-t border-line bg-bg md:static md:mx-0 md:px-0 md:pb-0 md:pt-6 md:bg-transparent flex flex-wrap items-center gap-3">
                <Button type="submit" disabled={!perfilId || gerandoCaso} aria-busy={gerandoCaso} className="w-full md:w-auto">
                  {gerandoCaso ? (
                    <>
                      <LoaderCircle size={16} strokeWidth={1.5} aria-hidden className="animate-spin motion-reduce:animate-none" />
                      Gerando paciente…
                    </>
                  ) : (
                    <>
                      <Sparkle size={16} strokeWidth={1.5} aria-hidden className="transition-colors group-hover:group-enabled:text-accent-inverse" />
                      Gerar paciente e iniciar
                    </>
                  )}
                </Button>
                <span role="status" className="sr-only">{gerandoCaso ? "Gerando paciente, aguarde." : ""}</span>
                <Link href="/" className={`${estiloBotao("ghost")} hidden! md:inline-flex!`}>Cancelar</Link>
              </div>
            </>
          )}
        </form>
      </div>
    </>
  );
}
