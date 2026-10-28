import { ButtonHTMLAttributes } from "react";

type Variante = "primary" | "secondary" | "ghost";

const VARIANTES: Record<Variante, string> = {
  // primario em fg: a lima fica so na assinatura (ia, foco, progresso)
  primary: "border-transparent bg-fg text-bg hover:bg-fg/80",
  secondary: "bg-transparent border-line-strong text-fg hover:border-fg",
  ghost: "border-transparent bg-transparent text-fg-muted hover:bg-surface-raised hover:text-fg",
};

// alvo de toque de 44px no celular; no desktop 36px (32px no pequeno)
export function estiloBotao(variante: Variante = "primary", pequeno = false) {
  const tamanho = pequeno ? "md:h-8 px-3 text-[13px]" : "md:h-9 px-4 text-[14px]";
  return `group inline-flex items-center justify-center gap-2 h-11 ${tamanho} rounded-md border font-medium leading-none whitespace-nowrap transition-colors cursor-pointer disabled:opacity-45 disabled:cursor-not-allowed ${VARIANTES[variante]}`;
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variante;
}

export function Button({ variant = "primary", className = "", children, ...props }: ButtonProps) {
  return (
    <button className={`${estiloBotao(variant)} ${className}`} {...props}>
      {children}
    </button>
  );
}
