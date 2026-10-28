import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export function Button({ variant = "primary", className = "", children, ...props }: ButtonProps) {
  const baseStyles = "group h-11 md:h-9 px-4 font-medium text-[14px] rounded-md border border-transparent whitespace-nowrap transition-colors flex items-center justify-center gap-2 disabled:opacity-45 disabled:cursor-not-allowed cursor-pointer";
  
  const variants = {
    // primario em fg: a lima fica so na assinatura (ia, foco, progresso)
    primary: "bg-fg text-bg hover:bg-fg/80",
    secondary: "bg-transparent border-line-strong text-fg hover:border-fg",
    ghost: "bg-transparent text-fg-muted hover:bg-surface-raised hover:text-fg",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`} 
      {...props}
    >
      {children}
    </button>
  );
}