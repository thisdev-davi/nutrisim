"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, LoaderCircle } from "lucide-react";
import type { ZodType } from "zod";
import { useAuth } from "@/components/providers/AuthProvider";
import type { Erro } from "@/lib/api";
import { formatZodErrors } from "@/lib/validation";
import { cadastroSchema, loginSchema, type CadastroFormData } from "@/schemas/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";

type Modo = "entrar" | "criar";
type Campo = "nome" | "email" | "senha";

const TEXTOS = {
  criar: {
    titulo: "Crie sua conta",
    subtitulo: "Para guardar suas sessões e retomar de onde parou.",
    acao: "Criar conta e entrar",
    enviando: "Criando conta…",
    feito: "Conta criada",
    pergunta: "Já tem conta?",
    trocar: "Entrar",
    outra: "/login",
  },
  entrar: {
    titulo: "Entre na sua conta",
    subtitulo: "Retome suas sessões de onde parou.",
    acao: "Entrar",
    enviando: "Entrando…",
    feito: "Login realizado",
    pergunta: "Ainda não tem conta?",
    trocar: "Criar conta",
    outra: "/cadastro",
  },
};

const MENSAGENS: Record<string, string> = {
  credenciais_invalidas: "E-mail ou senha incorretos. Confira os dois e tente de novo.",
  email_em_uso: "Este e-mail já tem conta. Entre com ele ou use outro e-mail.",
};

const SELO = "inline-flex items-center h-6 px-[10px] rounded-full border text-[12px] font-medium leading-none whitespace-nowrap";

// login e cadastro sao a mesma tela; muda o modo e os textos
export function FormularioAuth({ modo, email = "", redirect }: { modo: Modo; email?: string; redirect?: string }) {
  const { login, cadastro } = useAuth();
  const router = useRouter();
  const form = useRef<HTMLFormElement>(null);
  const criar = modo === "criar";
  const t = TEXTOS[modo];
  const schema = criar ? cadastroSchema : loginSchema;
  // so caminho interno, para o ?redirect= nao mandar para outro site
  const destino = redirect?.startsWith("/") && !redirect.startsWith("//") ? redirect : "/caso/novo";
  const sufixo = redirect ? `?redirect=${encodeURIComponent(redirect)}` : "";

  const [dados, setDados] = useState({ nome: "", email, senha: "" });
  const [erros, setErros] = useState<Partial<Record<Campo, string>>>({});
  const [erro, setErro] = useState<Erro | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [feito, setFeito] = useState(false);
  const [verSenha, setVerSenha] = useState(false);

  function validar(campo: Campo, valor: string) {
    const r = (schema.shape as Partial<Record<Campo, ZodType>>)[campo]!.safeParse(valor);
    setErros((e) => ({ ...e, [campo]: r.success ? undefined : r.error.issues[0].message }));
  }

  function mudar(campo: Campo, valor: string) {
    setDados((d) => ({ ...d, [campo]: valor }));
    if (erros[campo]) validar(campo, valor);
  }

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    const r = schema.safeParse(dados);
    if (!r.success) {
      const novos = formatZodErrors(r.error);
      setErros(novos);
      form.current?.querySelector<HTMLInputElement>(`#${(["nome", "email", "senha"] as const).find((c) => novos[c])}`)?.focus();
      return;
    }

    setEnviando(true);
    try {
      if (criar) await cadastro(r.data as CadastroFormData);
      else await login(r.data);
      setFeito(true);
      // o alerta fica cerca de 1s antes de seguir
      setTimeout(() => router.push(destino), 1000);
    } catch (err) {
      setErro(err as Erro);
      // senha errada: limpa a senha e mantem o e-mail
      if ((err as Erro).codigo === "credenciais_invalidas") setDados((d) => ({ ...d, senha: "" }));
    } finally {
      setEnviando(false);
    }
  }

  const campo = (c: Campo) => ({
    id: c,
    value: dados[c],
    error: erros[c],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => mudar(c, e.target.value),
    onBlur: () => validar(c, dados[c]),
  });

  return (
    <div className="grid w-full min-h-dvh grid-rows-[112px_1fr] md:grid-rows-none md:grid-cols-[minmax(360px,32%)_minmax(0,1fr)] bg-bg text-fg">
      <aside className="escuro relative overflow-hidden flex flex-col items-center justify-center gap-6 p-4 md:px-8 md:py-12 bg-bg text-fg text-center border-b md:border-b-0 md:border-r border-line">
        <span className="pontos" aria-hidden />
        <img src="/logo/nutrisim-escuro.svg" alt="NutriSim" className="relative h-6 md:h-8 w-auto" />
        <p className="relative hidden md:block m-0 max-w-[16ch] font-display text-[32px] leading-[38px] tracking-[-0.04em] text-balance">
          Pratique a consulta nutricional antes do consultório.
        </p>
        <div className="relative hidden md:flex flex-wrap justify-center gap-2">
          <span className={`${SELO} border-transparent bg-accent-soft text-accent`}>IA · representa o paciente</span>
          <span className={`${SELO} border-line-strong text-fg-muted`}>Motor · calcula a fisiologia</span>
        </div>
      </aside>

      <main className="flex items-start md:items-center justify-center px-4 py-8 md:px-8 md:py-12">
        <div className="w-full max-w-[360px] flex flex-col gap-6">
          {feito ? (
            <>
              <div role="status">
                <Alert type="success" title={t.feito}>Abrindo o NutriSim…</Alert>
              </div>
              <p className="m-0 text-[14px] leading-5 text-fg-muted">
                Se nada acontecer, <Link href={destino} className="text-fg underline underline-offset-3">abra o NutriSim</Link>.
              </p>
            </>
          ) : (
            <>
              <div className="flex flex-col gap-2 text-center">
                <h1 className="m-0 font-display font-medium text-[28px] leading-[34px] tracking-[-0.02em]">{t.titulo}</h1>
                <p className="m-0 text-[14px] leading-5 text-fg-muted">{t.subtitulo}</p>
              </div>

              <form ref={form} noValidate onSubmit={enviar} aria-label={t.titulo}>
                <fieldset disabled={enviando} className="m-0 p-0 border-0 min-w-0 flex flex-col gap-4">
                  {erro && (
                    <Alert
                      type="danger"
                      action={
                        erro.codigo === "email_em_uso" && (
                          <Link href={`/login?${new URLSearchParams({ email: dados.email, ...(redirect && { redirect }) })}`} className="text-[13px] font-medium underline">
                            Entrar com este e-mail
                          </Link>
                        )
                      }
                    >
                      {MENSAGENS[erro.codigo] ?? erro.mensagem}
                    </Alert>
                  )}

                  {criar && <Input label="Nome" type="text" autoComplete="name" placeholder="Ana Lima" {...campo("nome")} />}
                  <Input label="E-mail" type="email" autoComplete="email" placeholder="voce@exemplo.com" {...campo("email")} />
                  <Input
                    label="Senha"
                    type={verSenha ? "text" : "password"}
                    autoComplete={criar ? "new-password" : "current-password"}
                    helpText={criar ? "Use pelo menos 8 caracteres." : undefined}
                    {...campo("senha")}
                  >
                    <button
                      type="button"
                      className="grid place-items-center size-11 md:size-9 rounded-md text-fg-muted transition-colors hover:bg-surface-raised hover:text-fg cursor-pointer"
                      aria-label={verSenha ? "Ocultar senha" : "Mostrar senha"}
                      aria-pressed={verSenha}
                      onClick={() => setVerSenha(!verSenha)}
                    >
                      {verSenha ? <EyeOff size={16} strokeWidth={1.5} aria-hidden /> : <Eye size={16} strokeWidth={1.5} aria-hidden />}
                    </button>
                  </Input>

                  <Button type="submit" className="mt-2 w-full" aria-busy={enviando}>
                    {enviando && <LoaderCircle size={16} strokeWidth={1.5} aria-hidden className="animate-spin motion-reduce:animate-none" />}
                    {enviando ? t.enviando : t.acao}
                  </Button>
                  <span className="sr-only" role="status">{enviando ? `${t.enviando.slice(0, -1)}, aguarde.` : ""}</span>

                  {criar && (
                    <p className="m-0 text-[13px] leading-5 text-fg-muted">
                      Guardamos só seu nome, e-mail e senha, para você entrar e retomar suas sessões. Nada disso é compartilhado.
                    </p>
                  )}
                </fieldset>
              </form>

              <p className="m-0 text-fg-muted">
                {t.pergunta}{" "}
                <Link href={`${t.outra}${sufixo}`} className="font-medium text-fg underline underline-offset-3">{t.trocar}</Link>
              </p>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
