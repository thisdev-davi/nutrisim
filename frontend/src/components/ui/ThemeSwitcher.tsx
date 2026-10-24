"use client"

import { useTheme } from "next-themes"
import { useEffect, useState } from "react";

/**
 * Botão para trocar o tema do site
 */
const ThemeSwitch = () => {
  const [mounted, setMounted] = useState(false);
  const {resolvedTheme, setTheme} = useTheme();

useEffect(() => {
  // eslint-disable-next-line react-hooks/set-state-in-effect
  setMounted(true);
}, []);

  if(!mounted) {
    return null;
  }

  return (
      <div>
          <button onClick={() => setTheme(resolvedTheme == "dark" ? "light" : "dark")}>
            Trocar Tema ({resolvedTheme})
          </button>
      </div>
  );
};

export default ThemeSwitch;