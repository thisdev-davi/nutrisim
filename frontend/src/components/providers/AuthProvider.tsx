"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { setCookie, deleteCookie, getCookie } from "cookies-next";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { api, COOKIE_TOKEN } from "@/lib/api";

interface Usuario {
  id: string;
  nome: string;
  email: string;
}

interface AuthContextType {
  usuario: Usuario | null;
  carregando: boolean;
  // so guardam a sessao: quem chama mostra o sucesso e navega
  login: (dados: { email: string; senha: string }) => Promise<void>;
  cadastro: (dados: { nome: string; email: string; senha: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);
  const router = useRouter();
  const queryClient = useQueryClient();

  useEffect(() => {
    async function carregarUsuario() {
      const token = getCookie(COOKIE_TOKEN);
      
      if (token) {
        try {
          setUsuario(await api<Usuario>("/auth/eu"));
        } catch {
          // o 401 o api.ts ja trata, guardando o ?redirect=; falha de rede nao desloga
          setUsuario(null);
        }
      }
      setCarregando(false);
    }

    carregarUsuario();
  }, []);

  async function login(credenciais: { email: string; senha: string }) {
    const data = await api<{ token: string; usuario: Usuario }>("/auth/login", { method: "POST", body: JSON.stringify(credenciais) });
    
    // o cookie dura o mesmo que o token do backend (8 h)
    setCookie(COOKIE_TOKEN, data.token, { maxAge: 60 * 60 * 8, path: "/" });
    setUsuario(data.usuario);
  }

  async function cadastro(dados: { nome: string; email: string; senha: string }) {
    const data = await api<{ token: string; usuario: Usuario }>("/auth/cadastro", { method: "POST", body: JSON.stringify(dados) });
    
    setCookie(COOKIE_TOKEN, data.token, { maxAge: 60 * 60 * 8, path: "/" });
    setUsuario(data.usuario);
  }

  function logout() {
    deleteCookie(COOKIE_TOKEN, { path: "/" });
    // o router.push nao recarrega: sem isso a proxima conta ve as sessoes desta
    queryClient.clear();
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