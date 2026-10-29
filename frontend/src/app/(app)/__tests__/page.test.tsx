import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import InicioPage from "../page";

jest.mock("../../../components/providers/AuthProvider", () => ({ useAuth: () => ({ usuario: { nome: "Ana Lima" } }) }));

const sessao = (id: string, nome: string, etapa: string) => ({
  id,
  etapa,
  perfil: "Adulto com hipertensão",
  dificuldade: "medio",
  paciente: { nome, idade: 45, queixa_principal: "q" },
  criada_em: "2026-10-21T12:00:00Z",
});

function renderizar(sessoes: unknown[]) {
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => sessoes });
  render(
    <QueryClientProvider client={new QueryClient()}>
      <InicioPage />
    </QueryClientProvider>
  );
}

describe("InicioPage", () => {
  it("retoma a mais nova e lista as outras", async () => {
    renderizar([sessao("s1", "João", "plano"), sessao("s2", "Maria", "anamnese")]);

    expect(await screen.findByRole("link", { name: "Continuar sessão" })).toHaveAttribute("href", "/sessoes/s1");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Olá, Ana. Retome João ou comece um paciente novo.");
    expect(screen.getByText("Etapa 3 de 5 · Plano alimentar")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Maria, 45 anos/ })).toHaveAttribute("href", "/sessoes/s2");
  });

  it("sem sessoes so convida a comecar", async () => {
    renderizar([]);

    expect(await screen.findByText("Comece seu primeiro paciente.")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Continuar sessão" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Nova sessão/ })).toHaveAttribute("href", "/caso/novo");
  });
});
