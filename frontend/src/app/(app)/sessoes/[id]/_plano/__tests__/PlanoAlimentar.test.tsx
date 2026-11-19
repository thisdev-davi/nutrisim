import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "../../../../../../lib/api";
import { PlanoAlimentar } from "../PlanoAlimentar";

// caminho relativo: o jest.mock com "@/" nao resolve dentro de "(app)"
jest.mock("../../../../../../lib/api", () => ({ api: jest.fn() }));

const ARROZ = { id: 1, nome: "Arroz, integral, cozido", kcal: 124 };

// resposta do motor para o almoco com arroz: um alerta no item e um do dia
const plano = (gramas: number) => ({
  refeicoes: [{ nome: "Almoço", itens: [{ alimento_id: 1, gramas, nome: ARROZ.nome, kcal: 124 * gramas / 100 }], composicao: { valores: { kcal: 124 * gramas / 100 } } }],
  total: { valores: { kcal: 124 * gramas / 100, proteina: 2.6 } },
  get_kcal: 2000,
  adequacao: { proteina: { consumo: 2.6, referencia: 56, percentual: 5, classificacao: "abaixo" } },
  violacoes: [
    { tipo: "alimento_evitado", mensagem: "arroz entra em cereais, que o caso pede para evitar", refeicao: "Almoço", alimento_id: 1 },
    { tipo: "orcamento", mensagem: "custo passa do orcamento", refeicao: null, alimento_id: null },
  ],
  custo_diario_reais: 1.5,
  sem_preco: ["Sal"],
});

const puts = () => jest.mocked(api).mock.calls.filter(([, init]) => init?.method === "PUT");

function renderizar() {
  const queryClient = new QueryClient();
  queryClient.setQueryData(["sessao", "s1"], { id: "s1", etapa: "plano" });
  render(
    <QueryClientProvider client={queryClient}>
      <PlanoAlimentar sessaoId="s1" />
    </QueryClientProvider>
  );
  return queryClient;
}

describe("PlanoAlimentar", () => {
  beforeEach(() => {
    jest.mocked(api).mockReset();
    jest.mocked(api).mockImplementation(async (caminho, init) => {
      if (caminho.startsWith("/alimentos")) return [ARROZ];
      if (init?.method === "PUT") return plano(JSON.parse(init.body as string).refeicoes.find((r: { nome: string }) => r.nome === "Almoço").itens[0].gramas);
      if (caminho.endsWith("/encaminhar")) return { etapa: "retorno" };
      throw { codigo: "plano_nao_encontrado", mensagem: "nenhum plano salvo" };
    });
  });

  it("busca na TACO, salva com debounce e mostra o alerta junto do item", async () => {
    const user = userEvent.setup();
    renderizar();

    // 404 antes do primeiro PUT: tela vazia, sem erro
    await user.type(await screen.findByLabelText("Adicionar alimento em Almoço"), "arroz");
    expect(await screen.findByRole("option", { name: /Arroz, integral/ })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    await user.keyboard("{Enter}");

    const item = (await screen.findByText(/caso pede para evitar/)).closest("li")!;
    expect(within(item).getByText(ARROZ.nome)).toBeInTheDocument();
    expect(screen.getByText("custo passa do orcamento").closest("aside")).toBeInTheDocument();
    expect(screen.getByText(/sem preço para Sal/)).toBeInTheDocument();
    expect(screen.getByText("124 de 2.000 kcal do GET (6%)")).toBeInTheDocument();
    expect(JSON.parse(puts()[0][1]!.body as string)).toEqual(expect.objectContaining({ refeicoes: expect.arrayContaining([{ nome: "Almoço", itens: [{ alimento_id: 1, gramas: 100 }] }]) }));

    // varias teclas seguidas viram um PUT so, com o valor final
    const gramas = screen.getByLabelText(`Gramas de ${ARROZ.nome}`);
    await user.clear(gramas);
    await user.type(gramas, "150");
    expect(await screen.findByText("186 de 2.000 kcal do GET (9%)")).toBeInTheDocument();
    expect(puts()).toHaveLength(2);
    expect(puts()[1][1]!.body).toContain('"gramas":150');
  });

  it("encaminha o paciente com o motivo e vai para o retorno", async () => {
    HTMLDialogElement.prototype.showModal = jest.fn(); // o jsdom nao implementa o dialog
    const user = userEvent.setup();
    const queryClient = renderizar();

    await user.click(await screen.findByRole("button", { name: "Encaminhar o paciente" }));
    const enviar = screen.getByRole("button", { name: "Encaminhar", hidden: true });
    expect(enviar).toBeDisabled();
    await user.type(screen.getByLabelText("Motivo do encaminhamento"), "  glicemia muito alta, precisa do medico ");
    await user.click(enviar);

    await waitFor(() => expect(queryClient.getQueryData(["sessao", "s1"])).toEqual({ id: "s1", etapa: "retorno" }));
    expect(api).toHaveBeenCalledWith("/sessoes/s1/plano/encaminhar", { method: "POST", body: JSON.stringify({ motivo: "glicemia muito alta, precisa do medico" }) });
  });
});
