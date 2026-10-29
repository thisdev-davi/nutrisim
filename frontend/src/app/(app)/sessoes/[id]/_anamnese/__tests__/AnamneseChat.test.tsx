import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "../../../../../../lib/api";
import { enviarMensagem } from "../../../../../../lib/sse";
import { AnamneseChat } from "../AnamneseChat";

// caminho relativo: o jest.mock com "@/" nao resolve dentro de "(app)"
jest.mock("../../../../../../lib/api", () => ({ api: jest.fn() }));
jest.mock("../../../../../../lib/sse", () => ({ enviarMensagem: jest.fn() }));

const SESSAO = { id: "s1", etapa: "anamnese", paciente: { nome: "João", idade: 50, queixa_principal: "pressao alta" }, mensagens: [] };

describe("AnamneseChat", () => {
  it("mostra o erro do paciente, tira a pergunta nao salva e reenvia no tentar de novo", async () => {
    jest.mocked(api).mockResolvedValue(SESSAO); // o backend nao salvou nada
    jest.mocked(enviarMensagem)
      .mockRejectedValueOnce({ codigo: "paciente_indisponivel", mensagem: "o paciente nao conseguiu responder" })
      .mockImplementationOnce(async (_id, _texto, aoTrecho) => {
        aoTrecho("Trabalho de noite.");
        return "9";
      });
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={new QueryClient()}>
        <AnamneseChat sessaoId="s1" />
      </QueryClientProvider>
    );

    await user.type(await screen.findByLabelText("Mensagem para o paciente"), "Qual sua rotina?{Enter}");

    expect(await screen.findByRole("alert")).toHaveTextContent("o paciente nao conseguiu responder");
    expect(screen.queryByText("Qual sua rotina?")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Mensagem para o paciente")).toBeEnabled(); // nao trava no "respondendo"

    await user.click(screen.getByRole("button", { name: "Tentar de novo" }));

    expect(await screen.findByText("Trabalho de noite.")).toBeInTheDocument();
    expect(screen.getByText("Qual sua rotina?")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(jest.mocked(enviarMensagem).mock.calls[1][1]).toBe("Qual sua rotina?");
    await waitFor(() => expect(screen.getByLabelText("Mensagem para o paciente")).toBeEnabled());
  });
});
