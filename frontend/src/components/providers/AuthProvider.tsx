"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { setCookie, deleteCookie, getCookie } from "cookies-next";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface Usuario {
  id: string;
  nome: string;
  email: string;
}

interface AuthContextType {
  usuario: Usuario | null;
  carregando: boolean;
  login: (dados: { email: string; senha: string }, redirectTo?: string) => Promise<void>;
  cadastro: (dados: { nome: string; email: string; senha: string }, redirectTo?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function carregarUsuario() {
      const token = getCookie("nutrisim_token");
      
      if (token) {
        try {
          const { data } = await api.get<Usuario>("/api/auth/eu");
          setUsuario(data);
        } catch {
          logout();
        }
      }
      setCarregando(false);
    }

    carregarUsuario();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(credenciais: { email: string; senha: string }, redirectTo = "/caso/novo") {
    const { data } = await api.post("/api/auth/login", credenciais);
    
    // Guarda o token nos cookies por 7 dias
    setCookie("nutrisim_token", data.token, { maxAge: 60 * 60 * 24 * 7, path: "/" });
    setUsuario(data.usuario);
    router.push(redirectTo);
  }

  async function cadastro(dados: { nome: string; email: string; senha: string }, redirectTo = "/caso/novo") {
    const { data } = await api.post("/api/auth/cadastro", dados);
    
    setCookie("nutrisim_token", data.token, { maxAge: 60 * 60 * 24 * 7, path: "/" });
    setUsuario(data.usuario);
    router.push(redirectTo);
  }

  function logout() {
    deleteCookie("nutrisim_token", { path: "/" });
    setUsuario(null);
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ usuario, carregando, login, cadastro, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook customizado para usar a autenticação de forma simples em qualquer componente
export const useAuth = () => useContext(AuthContext);