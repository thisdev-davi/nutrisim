"use client"

import { useTheme } from "next-themes"
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

/**
 * Botão para trocar o tema do site
 */
const ThemeSwitch = ({ className = "" }: { className?: string }) => {
  const [mounted, setMounted] = useState(false);
  const {resolvedTheme, setTheme} = useTheme();

useEffect(() => {
  // eslint-disable-next-line react-hooks/set-state-in-effect
  setMounted(true);
}, []);

  // guarda o espaco do botao ate saber o tema, sem pular o layout
  if(!mounted) {
    return <span className={className} />;
  }

  const escuro = resolvedTheme === "dark";
  const rotulo = escuro ? "Usar tema claro" : "Usar tema escuro";
  const Icone = escuro ? Moon : Sun;

  return (
    <button type="button" aria-label={rotulo} title={rotulo} className={className} onClick={() => setTheme(escuro ? "light" : "dark")}>
      <Icone size={16} strokeWidth={1.5} aria-hidden />
    </button>
  );
};

export default ThemeSwitch;
