"use client"

import { useTheme } from "next-themes"
import { useEffect, useState } from "react";

/**
 * Botão para trocar o tema do site
 */
const ThemeSwitch = () => {
  const [mounted, setMounted] = useState(false);
  const {theme, setTheme} = useTheme();

  useEffect(() => {
    setMounted(true);
  }, []);

  if(!mounted) {
    return;
  }

  return (
      <div>
          <button onClick={() => setTheme(theme == "dark" ? "light" : "dark")}>
            Trocar Tema ({theme})
          </button>
      </div>
  );
};

export default ThemeSwitch;