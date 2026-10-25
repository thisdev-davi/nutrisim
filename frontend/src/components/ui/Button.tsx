import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export function Button({ variant = "primary", className = "", children, ...props }: ButtonProps) {
  const baseStyles = "h-11 px-4 font-medium text-[15px] rounded-md transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer";
  
  const variants = {
    primary: "bg-accent text-on-accent hover:bg-accent-hover",
    secondary: "bg-transparent border border-line-strong text-fg hover:bg-surface-raised",
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