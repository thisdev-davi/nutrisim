import { deleteCookie, getCookie } from "cookies-next";
import { env } from "@/lib/env";

export interface Erro {
  codigo: string;
  mensagem: string;
}

// gravado pelo AuthProvider no login; o proxy.ts le o mesmo cookie
export const COOKIE_TOKEN = "nutrisim_token";

// toda chamada ao backend passa aqui: manda o bearer e devolve o erro do contrato
export async function requisitar(caminho: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const t = getCookie(COOKIE_TOKEN);
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (init.body) headers.set("Content-Type", "application/json");
  const resp = await fetch(`${env.api.url}/api${caminho}`, { ...init, headers });
  if (resp.ok) return resp;
  if (resp.status === 401) {
    // token vencido: limpa e manda pro login, voltando para onde estava
    deleteCookie(COOKIE_TOKEN, { path: "/" });
    if (!location.pathname.startsWith("/login")) location.href = `/login?redirect=${encodeURIComponent(location.pathname)}`;
  }
  const corpo = await resp.json().catch(() => null);
  throw (corpo?.erro ?? { codigo: `http_${resp.status}`, mensagem: "Algo deu errado. Tente de novo." }) as Erro;
}

export async function api<T>(caminho: string, init?: RequestInit): Promise<T> {
  return (await requisitar(caminho, init)).json();
}
