"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { env } from "@/lib/env";

// ---------------------------------------------------------------------------
// Tipos espelhando o contrato do backend (backend/app/schemas/api.py)
// ---------------------------------------------------------------------------

interface Perfil {
  id: string;
  nome: string;
  descricao: string;
}

type Dificuldade = "facil" | "medio" | "dificil";

interface Opcoes {
  perfis: Perfil[];
  dificuldades: Dificuldade[];
}

interface NovaSessao {
  perfil_id: string;
  dificuldade: Dificuldade;
}

interface Paciente {
  nome: string;
  idade: number;
  queixa_principal: string;
}

interface Sessao {
  id: string;
  etapa: string;
  perfil_id: string;
  dificuldade: Dificuldade;
  paciente: Paciente;
  mensagens: unknown[];
}

interface RespostaErro {
  erro: {
    codigo: string;
    mensagem: string;
  };
}

// ---------------------------------------------------------------------------
// Funções de API
// ---------------------------------------------------------------------------

async function fetchOpcoes(): Promise<Opcoes> {
  const resp = await fetch(`${env.api.url}/api/perfis`);
  if (!resp.ok) {
    throw new Error("Não foi possível carregar os perfis disponíveis.");
  }
  return resp.json();
}

async function postCriarSessao(dados: NovaSessao): Promise<Sessao> {
  const resp = await fetch(`${env.api.url}/api/sessoes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });

  if (!resp.ok) {
    const errorBody = (await resp.json().catch(() => null)) as RespostaErro | null;
    throw new Error(errorBody?.erro?.mensagem || "Falha ao criar o caso clínico.");
  }

  return resp.json();
}

const ROTULOS_DIFICULDADE: Record<Dificuldade, string> = {
  facil: "Fácil",
  medio: "Médio",
  dificil: "Difícil",
};

// ---------------------------------------------------------------------------
// Componente
// ---------------------------------------------------------------------------

export default function NovoCasoPage() {
  const router = useRouter();

  const [perfilId, setPerfilId] = useState("");
  const [dificuldade, setDificuldade] = useState<Dificuldade | "">("");

  // 1. Carrega perfis e dificuldades via useQuery
  const {
    data: opcoes,
    isLoading: carregandoOpcoes,
    error: erroCarregar,
    refetch: recarregarOpcoes,
  } = useQuery({
    queryKey: ["perfis-e-dificuldades"],
    queryFn: fetchOpcoes,
  });

  // 2. Cria a sessão via useMutation
  const {
    mutate: gerarCaso,
    isPending: gerandoCaso,
    error: erroCriar,
    reset: limparErroCriar,
  } = useMutation({
    mutationFn: postCriarSessao,
    onSuccess: (sessao) => {
      router.push(`/sessoes/${sessao.id}`);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!perfilId || !dificuldade || gerandoCaso) return;

    limparErroCriar();
    gerarCaso({
      perfil_id: perfilId,
      dificuldade: dificuldade as Dificuldade,
    });
  }

  function handleTentarNovamente() {
    if (!perfilId || !dificuldade) return;
    limparErroCriar();
    gerarCaso({
      perfil_id: perfilId,
      dificuldade: dificuldade as Dificuldade,
    });
  }

  const perfilSelecionado = opcoes?.perfis.find((p) => p.id === perfilId);
  const podeCriar = perfilId !== "" && dificuldade !== "" && !gerandoCaso;

  return (
    <main
      style={{
        maxWidth: 600,
        width: "100%",
        margin: "0 auto",
        padding: "24px 16px",
        boxSizing: "border-box",
      }}
    >
      <header>
        <p style={{ margin: "0 0 8px" }}>Etapa 1 de 5 · Seleção de Caso</p>
        <h1 style={{ margin: "0 0 8px" }}>Novo caso clínico</h1>
        <p style={{ margin: "0 0 24px" }}>
          Selecione o perfil do paciente e a dificuldade para iniciar o atendimento.
        </p>
      </header>

      {/* Estado de carregamento inicial */}
      {carregandoOpcoes && <p role="status">Carregando opções disponíveis…</p>}

      {/* Estado de erro ao carregar opções */}
      {erroCarregar && (
        <section role="alert" style={{ marginBottom: 24 }}>
          <p style={{ color: "red", margin: "0 0 8px" }}>
            Erro ao carregar opções: {erroCarregar instanceof Error ? erroCarregar.message : "Erro desconhecido."}
          </p>
          <button type="button" onClick={() => recarregarOpcoes()}>
            Tentar carregar novamente
          </button>
        </section>
      )}

      {/* Formulário */}
      {opcoes && (
        <form onSubmit={handleSubmit}>
          {/* Seletor de Perfil */}
          <fieldset style={{ border: "none", padding: 0, margin: "0 0 20px" }}>
            <legend>
              <strong>Perfil do paciente</strong>
            </legend>

            <label
              htmlFor="perfil"
              style={{ display: "block", marginTop: 8, marginBottom: 4 }}
            >
              Patologia ou objetivo
            </label>
            <select
              id="perfil"
              value={perfilId}
              onChange={(e) => setPerfilId(e.target.value)}
              disabled={gerandoCaso}
              required
              style={{ width: "100%", minHeight: 44, padding: "8px 12px", boxSizing: "border-box" }}
            >
              <option value="">Selecione um perfil</option>
              {opcoes.perfis.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nome}
                </option>
              ))}
            </select>

            {perfilSelecionado && (
              <p style={{ fontSize: 14, margin: "6px 0 0" }}>
                {perfilSelecionado.descricao}
              </p>
            )}
          </fieldset>

          {/* Seletor de Dificuldade */}
          <fieldset style={{ border: "none", padding: 0, margin: "0 0 20px" }}>
            <legend>
              <strong>Dificuldade</strong>
            </legend>

            <label
              htmlFor="dificuldade"
              style={{ display: "block", marginTop: 8, marginBottom: 4 }}
            >
              Nível de dificuldade
            </label>
            <select
              id="dificuldade"
              value={dificuldade}
              onChange={(e) => setDificuldade(e.target.value as Dificuldade)}
              disabled={gerandoCaso}
              required
              style={{ width: "100%", minHeight: 44, padding: "8px 12px", boxSizing: "border-box" }}
            >
              <option value="">Selecione a dificuldade</option>
              {opcoes.dificuldades.map((d) => (
                <option key={d} value={d}>
                  {ROTULOS_DIFICULDADE[d] ?? d}
                </option>
              ))}
            </select>
          </fieldset>

          {/* Erro na criação do caso com opção de tentar de novo */}
          {erroCriar && (
            <div role="alert" style={{ margin: "16px 0", color: "red" }}>
              <p style={{ margin: "0 0 8px" }}>
                {erroCriar instanceof Error ? erroCriar.message : "Erro ao criar o caso."}
              </p>
              <div style={{ display: "flex", gap: 12 }}>
                <button
                  type="button"
                  onClick={handleTentarNovamente}
                  disabled={gerandoCaso}
                  style={{ minHeight: 44, padding: "8px 16px" }}
                >
                  Tentar de novo
                </button>
                <button type="button" onClick={limparErroCriar} style={{ minHeight: 44, padding: "8px 16px" }}>
                  Dispensar
                </button>
              </div>
            </div>
          )}

          {/* Botão de envio com estado de carregamento */}
          <div style={{ marginTop: 24 }}>
            <button
              type="submit"
              disabled={!podeCriar}
              style={{
                width: "100%",
                minHeight: 44,
                padding: "10px 24px",
                cursor: podeCriar ? "pointer" : "not-allowed",
              }}
            >
              {gerandoCaso ? "Gerando paciente e iniciando consulta…" : "Gerar paciente e iniciar consulta"}
            </button>
          </div>
        </form>
      )}
    </main>
  );
}
