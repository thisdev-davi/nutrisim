import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "../../../../../lib/api";
import { EtapaSessao } from "../EtapaSessao";

// caminho relativo: o jest.mock com "@/" nao resolve dentro de "(app)"
jest.mock("../../../../../lib/api", () => ({ api: jest.fn() }));

const SESSAO = { id: "s1", etapa: "anamnese", perfil_id: "p", dificuldade: "medio", paciente: { nome: "João", idade: 50, queixa_principal: "pressao alta" }, mensagens: [] };

const renderizar = () =>
  render(
    <QueryClientProvider client={new QueryClient()}>
      <EtapaSessao sessaoId="s1" />
    </QueryClientProvider>
  );

// o indicador aparece duas vezes (celular e desktop); vale o primeiro
const etapaAtual = () => screen.getAllByRole("listitem").find((li) => li.getAttribute("aria-current") === "step");

describe("EtapaSessao", () => {
  beforeEach(() => jest.mocked(api).mockReset());

  it.each([["retorno", "Retorno e feedback"]])("retoma a sessao em %s", async (etapa, nome) => {
    jest.mocked(api).mockResolvedValue({ ...SESSAO, etapa });
    renderizar();
    expect(await screen.findByText("Esta etapa ainda não está disponível")).toBeInTheDocument();
    expect(etapaAtual()).toHaveTextContent(nome);
  });

  it("encerra a anamnese e passa para o plano sem recarregar a sessao", async () => {
    jest.mocked(api).mockImplementation(async (caminho) => (caminho.endsWith("/encerrar") ? { etapa: "plano" } : caminho === "/perfis" ? {} : SESSAO));
    // o jsdom nao implementa o dialog
    HTMLDialogElement.prototype.showModal = jest.fn();
    HTMLDialogElement.prototype.close = jest.fn();
    const user = userEvent.setup();
    renderizar();
    await screen.findByText("João, 50 anos");
    expect(etapaAtual()).toHaveTextContent("Anamnese");

    await user.click(screen.getByRole("button", { name: "Montar o plano" }));
    await user.click(screen.getByRole("button", { name: "Encerrar e montar o plano", hidden: true }));

    expect(await screen.findByText("Esta etapa ainda não está disponível")).toBeInTheDocument();
    expect(etapaAtual()).toHaveTextContent("Plano alimentar");
    expect(jest.mocked(api).mock.calls.filter(([c]) => c === "/sessoes/s1")).toHaveLength(1);
  });
});
