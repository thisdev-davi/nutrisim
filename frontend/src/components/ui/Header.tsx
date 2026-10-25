import Link from "next/link";

interface HeaderProps {
  activeMenu?: "inicio" | "casos" | "historico";
}

const MENU = [["inicio", "Início"], ["casos", "Casos"], ["historico", "Histórico"]] as const;

export function Header({ activeMenu = "casos" }: HeaderProps) {
  return (
    <header className="border-b border-line shrink-0">
      <div className="w-full max-w-[1040px] mx-auto px-4 md:px-6 h-14 md:h-16 flex items-center justify-between">
        <Link href="/" aria-label="NutriSim, início">
          {/* troca a logo pela classe do next-themes, sem esperar montar */}
          <img src="/logo/nutrisim-escuro.svg" alt="NutriSim" className="h-7 object-contain [.light_&]:hidden" />
          <img src="/logo/nutrisim-claro.svg" alt="NutriSim" className="h-7 object-contain hidden [.light_&]:block" />
        </Link>

        <div className="hidden md:flex items-center gap-6">
          <nav className="flex gap-2">
            {MENU.map(([chave, rotulo]) => (
              <button
                key={chave}
                aria-current={activeMenu === chave ? "page" : undefined}
                className={`h-9 px-3 text-[14px] font-medium rounded-md transition-colors cursor-pointer ${activeMenu === chave ? "bg-surface-raised text-fg" : "text-fg-muted hover:bg-surface-raised hover:text-fg"}`}
              >
                {rotulo}
              </button>
            ))}
          </nav>

          <div className="w-px h-6 bg-line"></div>

          <div className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity">
            <span className="text-[14px] text-fg-muted">Perfil</span>
            <div className="w-6 h-6 rounded-full bg-surface-raised border border-line-strong"></div>
          </div>
        </div>
      </div>
    </header>
  );
}
