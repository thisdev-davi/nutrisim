import Link from "next/link";
import { estiloBotao } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";

// fora do (app): a rota pode nem existir, entao nao tem lateral
export default function NaoEncontrada() {
  return (
    <main className="relative isolate overflow-hidden flex-1 grid place-items-center min-h-dvh px-4 py-12 bg-bg text-fg">
      <span className="pontos -z-10" aria-hidden />
      <div className="flex flex-col items-center gap-3 text-center">
        <Logo />
        <span className="mt-4 text-[13px] leading-5 font-medium text-fg-muted">Erro 404</span>
        <h1 className="m-0 text-[18px] leading-[26px] font-semibold">Página não encontrada</h1>
        <p className="m-0 max-w-[40ch] text-fg-muted">O endereço pode estar errado ou a página ainda não existe.</p>
        <Link href="/" className={estiloBotao("primary", true)}>Voltar ao início</Link>
      </div>
    </main>
  );
}
