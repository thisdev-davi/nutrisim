import { env } from "@/lib/env";

export interface Erro {
  codigo: string;
  mensagem: string;
}

const CHAVE_TOKEN = "nutrisim:token";

// ponytail: token no localStorage ate a NS-036 trazer a tela de login
async function token(): Promise<string | null> {
  const salvo = localStorage.getItem(CHAVE_TOKEN);
  if (salvo) return salvo;
  // so em dev: entra (ou cadastra) com o usuario do .env.local, sem tela de login
  const email = process.env.NEXT_PUBLIC_DEV_EMAIL;
  const senha = process.env.NEXT_PUBLIC_DEV_SENHA;
  if (process.env.NODE_ENV !== "development" || !email || !senha) return null;
  const corpo = { method: "POST", headers: { "Content-Type": "application/json" } };
  let resp = await fetch(`${env.api.url}/api/auth/login`, { ...corpo, body: JSON.stringify({ email, senha }) });
  if (resp.status === 401) {
    resp = await fetch(`${env.api.url}/api/auth/cadastro`, { ...corpo, body: JSON.stringify({ nome: "Dev", email, senha }) });
  }
  if (!resp.ok) return null;
  const { token: novo } = await resp.json();
  localStorage.setItem(CHAVE_TOKEN, novo);
  return novo;
}

// toda chamada ao backend passa aqui: manda o bearer e devolve o erro do contrato
export async function requisitar(caminho: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const t = await token();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (init.body) headers.set("Content-Type", "application/json");
  const resp = await fetch(`${env.api.url}/api${caminho}`, { ...init, headers });
  if (resp.ok) return resp;
  if (resp.status === 401) localStorage.removeItem(CHAVE_TOKEN);
  const corpo = await resp.json().catch(() => null);
  throw (corpo?.erro ?? { codigo: `http_${resp.status}`, mensagem: "Algo deu errado. Tente de novo." }) as Erro;
}

export async function api<T>(caminho: string, init?: RequestInit): Promise<T> {
  return (await requisitar(caminho, init)).json();
}
