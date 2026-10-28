"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, PanelLeft, User } from "lucide-react";
import { Sidebar } from "@/components/ui/Sidebar";
import { Logo } from "@/components/ui/Logo";
import ThemeSwitch from "@/components/ui/ThemeSwitcher";

const CHAVE_RECOLHIDA = "nutrisim:lateral-recolhida";
const ICONE = "grid place-items-center size-11 md:size-8 rounded-md text-fg-muted transition-colors hover:bg-surface-raised hover:text-fg cursor-pointer";

function trilhaDe(pathname: string) {
  if (pathname === "/caso/novo") return "Nova sessão";
  if (pathname.startsWith("/sessoes/")) return "Sessão";
  return null;
}

// moldura fixa das telas logadas: lateral + barra do topo; no celular a lateral vira gaveta
export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const trilha = trilhaDe(pathname);
  const gaveta = useRef<HTMLDialogElement>(null);
  const [recolhida, setRecolhida] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setRecolhida(localStorage.getItem(CHAVE_RECOLHIDA) === "1");
  }, []);

  function alternarLateral() {
    setRecolhida(!recolhida);
    localStorage.setItem(CHAVE_RECOLHIDA, recolhida ? "0" : "1");
  }

  // fecha ao clicar fora (no backdrop) ou em qualquer link da gaveta
  function cliqueNaGaveta(e: React.MouseEvent<HTMLDialogElement>) {
    if (e.target === e.currentTarget || (e.target as HTMLElement).closest("a")) gaveta.current?.close();
  }

  return (
    <div className="flex h-dvh bg-chrome text-fg">
      <div className="hidden md:block flex-none h-dvh">
        <Sidebar id="menu" recolhida={recolhida} />
      </div>

      <div className="flex-1 min-w-0 flex flex-col">
        <header className="flex flex-none items-center gap-2 h-14 px-2 md:pl-3 md:pr-4 bg-chrome border-b border-line md:border-b-0">
          <button type="button" className={`${ICONE} hidden! md:grid!`} aria-controls="menu" aria-expanded={!recolhida} aria-label={recolhida ? "Expandir menu" : "Recolher menu"} onClick={alternarLateral}>
            <PanelLeft size={16} strokeWidth={1.5} aria-hidden />
          </button>
          <button type="button" className={`${ICONE} md:hidden!`} aria-label="Abrir menu" onClick={() => gaveta.current?.showModal()}>
            <Menu size={16} strokeWidth={1.5} aria-hidden />
          </button>
          <Link href="/" aria-label="NutriSim, início" className="md:hidden">
            <Logo />
          </Link>
          <nav aria-label="Trilha" className="hidden md:block min-w-0">
            <ol className="flex items-center gap-2 m-0 pl-1 list-none text-fg-muted text-[14px] leading-5 whitespace-nowrap">
              <li><Link href="/" className="hover:text-fg">Início</Link></li>
              {trilha && (
                <li className="before:content-['/'] before:mr-2 before:text-line-strong">
                  <span aria-current="page" className="text-fg">{trilha}</span>
                </li>
              )}
            </ol>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <ThemeSwitch className={ICONE} />
            {/* ponytail: avatar generico ate a NS-036 trazer o usuario logado */}
            <span aria-hidden className="grid place-items-center size-7 rounded-full border border-line bg-surface text-fg-muted">
              <User size={14} strokeWidth={1.5} />
            </span>
          </div>
        </header>

        <main className="flex-1 min-h-0 overflow-auto flex flex-col bg-bg md:border-t md:border-l md:border-line md:rounded-tl-lg md:bg-[radial-gradient(600px_circle_at_0_0,var(--glow),transparent)]">
          {children}
        </main>
      </div>

      <dialog
        ref={gaveta}
        aria-label="Menu"
        onClick={cliqueNaGaveta}
        className="m-0 h-full max-h-none w-[280px] max-w-[calc(100%-48px)] p-0 border-0 bg-chrome text-fg shadow-[var(--overlay)] backdrop:bg-black/60"
      >
        <Sidebar onFechar={() => gaveta.current?.close()} />
      </dialog>
    </div>
  );
}
