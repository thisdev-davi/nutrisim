"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { History, House, Plus, X } from "lucide-react";
import { estiloBotao } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";

// ponytail: historico aponta para # ate a rota existir
const ITENS = [
  { href: "/", rotulo: "Início", Icone: House },
  { href: "#", rotulo: "Histórico", Icone: History },
];

interface SidebarProps {
  id?: string;
  recolhida?: boolean;
  onFechar?: () => void;
}

export function Sidebar({ id, recolhida = false, onFechar }: SidebarProps) {
  const pathname = usePathname();
  const atual = (href: string) => (pathname === href ? "page" : undefined);
  const dica = (texto: string) => (recolhida ? texto : undefined);
  const rotulo = recolhida ? "sr-only" : "";
  const item = recolhida ? "w-10 justify-center px-0" : "px-2.5";

  return (
    <aside id={id} aria-label="Menu" className={`flex flex-col h-full bg-chrome ${onFechar ? "w-full" : recolhida ? "w-16" : "w-60"}`}>
      <div className={`flex items-center h-14 shrink-0 ${recolhida ? "justify-center" : "justify-between pl-5 pr-2"}`}>
        <Link href="/" aria-label="NutriSim, início">
          <Logo simbolo={recolhida} />
        </Link>
        {onFechar && (
          <button type="button" onClick={onFechar} aria-label="Fechar menu" className={estiloBotao("ghost") + " w-11 px-0"}>
            <X size={16} strokeWidth={1.5} aria-hidden />
          </button>
        )}
      </div>

      <div className={`flex flex-col gap-8 px-3 py-5 ${recolhida ? "items-center" : ""}`}>
        <Link
          href="/caso/novo"
          aria-current={atual("/caso/novo")}
          title={dica("Nova sessão")}
          className={`${estiloBotao("secondary", true)} aria-[current=page]:bg-surface-raised ${recolhida ? "w-10 px-0" : "w-full"}`}
        >
          <Plus size={16} strokeWidth={1.5} aria-hidden />
          <span className={rotulo}>Nova sessão</span>
        </Link>

        <nav aria-label="Principal" className="flex flex-col gap-0.5">
          {ITENS.map(({ href, rotulo: texto, Icone }) => (
            <Link
              key={texto}
              href={href}
              aria-current={atual(href)}
              title={dica(texto)}
              className={`group flex items-center gap-2.5 min-h-11 md:min-h-8 ${item} rounded-md text-fg-secondary text-[14px] leading-5 whitespace-nowrap transition-colors hover:bg-surface-hover hover:text-fg aria-[current=page]:bg-surface-hover aria-[current=page]:text-fg aria-[current=page]:font-medium`}
            >
              <Icone size={16} strokeWidth={1.5} aria-hidden className="shrink-0 transition-colors group-hover:text-accent" />
              <span className={rotulo}>{texto}</span>
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  );
}
