"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/providers/AuthProvider";
import type { Erro } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import { Sparkle } from "lucide-react";
import { cadastroSchema, CadastroFormData } from "@/schemas/auth";
import { formatZodErrors } from "@/lib/validation";

export default function CadastroPage() {
  const { cadastro } = useAuth();
  
  const [formData, setFormData] = useState<CadastroFormData>({
    nome: "",
    email: "",
    senha: "",
  });

  const [errosCampos, setErrosCampos] = useState<Record<string, string>>({});
  const [erroGeral, setErroGeral] = useState("");
  const [carregando, setCarregando] = useState(false);

  function handleChange(campo: keyof CadastroFormData, valor: string) {
    setFormData((prev) => ({ ...prev, [campo]: valor }));

    if (errosCampos[campo]) {
      setErrosCampos((prev) => {
        const novosErros = { ...prev };
        delete novosErros[campo];
        return novosErros;
      });
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErroGeral("");
    setErrosCampos({});

    const validacao = cadastroSchema.safeParse(formData);

    if (!validacao.success) {
      setErrosCampos(formatZodErrors(validacao.error));
      return;
    }

    setCarregando(true);
    try {
      await cadastro(validacao.data);
    } catch (err) {
      setErroGeral((err as Erro).mensagem || "Ocorreu um erro ao criar a conta.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-bg text-fg p-4">
      <div className="w-full max-w-sm bg-surface border border-line rounded-xl p-6 md:p-8 flex flex-col gap-6 shadow-sm">
        
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="w-10 h-10 bg-accent-soft text-accent rounded-full flex items-center justify-center mb-2">
            <Sparkle size={20} strokeWidth={1.5} />
          </div>
          <h1 className="text-[20px] font-semibold">Criar conta</h1>
          <p className="text-[14px] text-fg-muted">Junte-se ao NutriSim para simular consultas</p>
        </div>

        {erroGeral && (
          <Alert type="danger" title="Erro no cadastro">
            {erroGeral}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            id="nome"
            label="Nome completo"
            type="text"
            placeholder="Maria Silva"
            value={formData.nome}
            onChange={(e) => handleChange("nome", e.target.value)}
            error={errosCampos.nome}
            required
            disabled={carregando}
          />

          <Input
            id="email"
            label="E-mail"
            type="email"
            placeholder="seu@email.com"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            error={errosCampos.email}
            required
            disabled={carregando}
          />
          
          <Input
            id="senha"
            label="Senha"
            type="password"
            placeholder="Crie uma senha forte"
            value={formData.senha}
            onChange={(e) => handleChange("senha", e.target.value)}
            error={errosCampos.senha}
            required
            disabled={carregando}
          />

          <Button type="submit" disabled={carregando} className="mt-2 w-full">
            {carregando ? "Criando conta..." : "Criar conta"}
          </Button>
        </form>

        <p className="text-center text-[14px] text-fg-muted mt-2">
          Já possui uma conta?{" "}
          <Link href="/login" className="text-fg font-medium hover:text-accent transition-colors underline">
            Faça login
          </Link>
        </p>
      </div>
    </main>
  );
}