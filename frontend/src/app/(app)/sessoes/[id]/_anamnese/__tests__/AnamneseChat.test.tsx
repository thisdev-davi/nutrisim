import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "../../../../../../lib/api";
import { enviarMensagem } from "../../../../../../lib/sse";
import { AnamneseChat } from "../AnamneseChat";

// caminho relativo: o jest.mock com "@/" nao resolve dentro de "(app)"
jest.mock("../../../../../../lib/api", () => ({ api: jest.fn() }));
jest.mock("../../../../../../lib/sse", () => ({ enviarMensagem: jest.fn() }));

const SESSAO = { id: "s1", etapa: "anamnese", perfil_id: "adulto-diabetes-tipo2", dificuldade: "medio", paciente: { nome: "João", idade: 50, queixa_principal: "pressao alta" }, mensagens: [] };

describe("AnamneseChat", () => {
  it("devolve a pergunta nao salva ao campo e reenvia no tentar de novo", async () => {
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

    await screen.findByText("João, 50 anos"); // o campo ja aparece no carregamento, travado
    await user.type(screen.getByLabelText("Pergunta para o paciente"), "Qual sua rotina?{Enter}");

    expect(await screen.findByRole("alert")).toHaveTextContent("Sua pergunta continua no campo");
    expect(within(screen.getByRole("log")).queryByText("Qual sua rotina?")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Pergunta para o paciente")).toBeEnabled(); // nao trava no "respondendo"
    expect(screen.getByLabelText("Pergunta para o paciente")).toHaveValue("Qual sua rotina?");

    await user.click(screen.getByRole("button", { name: "Tentar de novo" }));

    expect(await screen.findByText("Trabalho de noite.")).toBeInTheDocument();
    expect(within(screen.getByRole("log")).getByText("Qual sua rotina?")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(jest.mocked(enviarMensagem).mock.calls[1][1]).toBe("Qual sua rotina?");
    await waitFor(() => expect(screen.getByLabelText("Pergunta para o paciente")).toBeEnabled());
  });
});
