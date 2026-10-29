"use client"; // <-- Faltava isso! Contextos só funcionam em Client Components

import Link from "next/link";
import ThemeSwitch from "@/components/ui/ThemeSwitch";
import { LogoutButton } from "@/components/ui/LogoutButton";
import { useAuth } from "@/components/providers/AuthProvider";

interface HeaderProps {
  activeMenu?: "inicio" | "casos" | "historico";
}

const MENU = [
  ["inicio", "Início", "/"],
  ["casos", "Novo Caso", "/sessoes/nova"],
  ["historico", "Histórico", "/historico"],
] as const;

export function Header({ activeMenu = "casos" }: HeaderProps) {
  // Puxamos também o "carregando" para lidar com o tempo de carregamento da página
  const { usuario, carregando } = useAuth();

  return (
    <header className="border-b-2 border-accent shrink-0 bg-surface">
      <div className="w-full max-w-[1040px] mx-auto px-4 md:px-6 h-14 md:h-16 flex items-center justify-between">
        <Link href="/" aria-label="NutriSim, início">
          <img
            src="/logo/nutrisim-escuro.svg"
            alt="NutriSim"
            className="h-7 object-contain [.light_&]:hidden"
          />
          <img
            src="/logo/nutrisim-claro.svg"
            alt="NutriSim"
            className="h-7 object-contain hidden [.light_&]:block"
          />
        </Link>

        <div className="hidden md:flex items-center gap-6">
          <nav className="flex gap-2">
            {MENU.map(([chave, rotulo, rota]) => {
              const isActive = activeMenu === chave;
              return (
                <Link
                  key={chave}
                  href={rota}
                  aria-current={isActive ? "page" : undefined}
                  className={`h-9 px-3 flex items-center text-[14px] font-medium rounded-md transition-colors cursor-pointer ${
                    isActive
                      ? "bg-surface-raised text-fg"
                      : "text-fg-muted hover:bg-surface-raised hover:text-fg"
                  }`}
                >
                  {rotulo}
                </Link>
              );
            })}
          </nav>

          <div className="w-px h-6 bg-line"></div>

          <div className="flex items-center gap-4">
            <ThemeSwitch />

            {/* Condicional que trata o estado de Loading e Usuário */}
            {carregando ? (
              <div className="flex items-center gap-3 animate-pulse">
                 <div className="w-16 h-4 bg-surface-raised rounded"></div>
                 <div className="w-20 h-8 bg-surface-raised rounded-md"></div>
              </div>
            ) : usuario ? (
              <div className="flex items-center gap-3">
                <span className="text-[14px] font-medium text-fg-muted">
                  {usuario.nome.split(" ")[0]}
                </span>
                <LogoutButton variant="ghost" />
              </div>
            ) : null}
            
            {/* O bloco antigo de "Perfil" (bolinha vazia) foi removido daqui para não duplicar */}
            
          </div>
        </div>
      </div>
    </header>
  );
}