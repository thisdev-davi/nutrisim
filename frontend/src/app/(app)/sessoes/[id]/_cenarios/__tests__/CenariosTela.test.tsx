import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "../../../../../../lib/api";
import { CenariosTela, type Cenarios } from "../CenariosTela";

// caminho relativo: o jest.mock com "@/" nao resolve dentro de "(app)"
jest.mock("../../../../../../lib/api", () => ({ api: jest.fn() }));

const adequacao = (percentual: number, classificacao: "abaixo" | "adequado" | "acima") => ({ consumo: 1, referencia: 1, percentual, classificacao, sem_dado: [] });

const CENARIOS: Cenarios = {
  ideal: { peso: [{ semana: 0, peso_kg: 90 }, { semana: 1, peso_kg: 89.4 }], adequacao: { sodio: adequacao(95, "adequado") } },
  realista: {
    peso: [{ semana: 0, peso_kg: 90 }, { semana: 1, peso_kg: 89.8 }],
    adequacao: { sodio: adequacao(140, "acima") },
    adesao: [{ refeicao: "Almoço", adesao: 0.6 }],
    substituicoes: [{ refeicao: "Almoço", original_id: 1, original: "Arroz integral", substituto_id: 2, substituto: "Arroz branco", motivo: "costume" }],
  },
  aviso: "Projeção simplificada, não substitui o acompanhamento.",
};

const renderizar = () =>
  render(
    <QueryClientProvider client={new QueryClient()}>
      <CenariosTela sessaoId="s1" />
    </QueryClientProvider>
  );

describe("CenariosTela", () => {
  beforeEach(() => jest.mocked(api).mockReset());

  it("mostra o carregamento e depois os dois cenarios com o aviso", async () => {
    jest.mocked(api).mockResolvedValue(CENARIOS);
    renderizar();
    expect(screen.getByText(/Gerando os cenários/)).toBeInTheDocument();

    expect(await screen.findByText(CENARIOS.aviso)).toBeInTheDocument();
    expect(jest.mocked(api)).toHaveBeenCalledWith("/sessoes/s1/cenarios", { method: "POST" });
    // alternativa em texto do grafico de peso
    const tabela = screen.getByRole("table");
    expect(within(tabela).getByRole("row", { name: "1 89,4 89,8" })).toBeInTheDocument();
    expect(screen.getByText("95% · adequado")).toBeInTheDocument();
    expect(screen.getByText("140% · acima")).toBeInTheDocument();
    expect(screen.getByText("adesão 60%")).toBeInTheDocument();
    expect(screen.getByText("Arroz branco", { exact: false })).toBeInTheDocument();
  });

  it("mostra o erro 503 e gera de novo no tentar de novo", async () => {
    jest.mocked(api)
      .mockRejectedValueOnce({ codigo: "cenario_nao_gerado", mensagem: "Não foi possível gerar os cenários agora." })
      .mockResolvedValueOnce(CENARIOS);
    const user = userEvent.setup();
    renderizar();

    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível gerar os cenários agora.");
    await user.click(screen.getByRole("button", { name: "Tentar de novo" }));

    expect(await screen.findByText(CENARIOS.aviso)).toBeInTheDocument();
    expect(jest.mocked(api)).toHaveBeenCalledTimes(2);
  });
});
