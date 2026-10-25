"use client";

import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

interface HeaderProps {
  mobileTitle?: string;
  activeMenu?: "inicio" | "casos" | "historico";
}

export function Header({ mobileTitle = "NutriSim", activeMenu = "casos" }: HeaderProps) {
  const router = useRouter();
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const logoSrc = mounted && theme === "light" 
    ? "/logo/nutrisim-claro.svg" 
    : "/logo/nutrisim-escuro.svg";

  return (
    <header className="border-b border-line bg-surface flex items-center justify-between px-4 md:px-8 h-14 md:h-16 shrink-0">

      <button 
        onClick={() => router.back()} 
        className="md:hidden text-[14px] text-fg-muted hover:text-fg cursor-pointer"
      >
        &lt; Voltar
      </button>

      <div className="hidden md:flex items-center">
        {mounted ? (
          <img 
            src={logoSrc} 
            alt="NutriSim" 
            className="h-7 object-contain cursor-pointer transition-opacity" 
            onClick={() => router.push('/')}
          />
        ) : (
          <div className="h-7 w-27.5" />
        )}
      </div>

      <div className="hidden md:flex items-center gap-6">
        <nav className="flex gap-2">
          <button 
            className={`h-9 px-3 text-[14px] font-medium rounded-md transition-colors cursor-pointer ${activeMenu === 'inicio' ? 'bg-accent-soft text-accent' : 'text-fg-muted hover:bg-surface-raised hover:text-fg'}`}
          >
            Início
          </button>
          <button 
            className={`h-9 px-3 text-[14px] font-medium rounded-md transition-colors cursor-pointer ${activeMenu === 'casos' ? 'bg-accent-soft text-accent' : 'text-fg-muted hover:bg-surface-raised hover:text-fg'}`}
          >
            Casos
          </button>
          <button 
            className={`h-9 px-3 text-[14px] font-medium rounded-md transition-colors cursor-pointer ${activeMenu === 'historico' ? 'bg-accent-soft text-accent' : 'text-fg-muted hover:bg-surface-raised hover:text-fg'}`}
          >
            Histórico
          </button>
        </nav>

        <div className="w-px h-6 bg-line"></div>

        <div className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity">
          <span className="text-[14px] text-fg-muted">Perfil</span>
          <div className="w-6 h-6 rounded-full bg-surface-raised border border-line-strong"></div>
        </div>
      </div>

      <span className="md:hidden text-[14px] font-medium text-fg">{mobileTitle}</span>
      <div className="md:hidden w-12.5"></div>
    </header>
  );
}