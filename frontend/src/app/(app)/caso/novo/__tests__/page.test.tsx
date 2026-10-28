import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import NovoCasoPage from "../page";

const push = jest.fn();
jest.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

const OPCOES = {
  perfis: [{ id: "adulto-diabetes-tipo2", nome: "Adulto com diabetes tipo 2", descricao: "Adulto de 40 a 65 anos." }],
  dificuldades: ["facil", "medio", "dificil"],
};

describe("NovoCasoPage", () => {
  it("so libera o envio com perfil escolhido e manda a dificuldade media por padrao", async () => {
    const fetchMock = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => OPCOES })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: "s1" }) });
    global.fetch = fetchMock;
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={new QueryClient()}>
        <NovoCasoPage />
      </QueryClientProvider>
    );

    const botao = await screen.findByRole("button", { name: /Gerar paciente e iniciar/ });
    expect(botao).toBeDisabled();
    expect(screen.getByRole("radio", { name: /Média/ })).toBeChecked();

    await user.selectOptions(screen.getByLabelText("Patologia ou objetivo"), "adulto-diabetes-tipo2");
    await user.click(botao);

    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ perfil_id: "adulto-diabetes-tipo2", dificuldade: "medio" });
    await waitFor(() => expect(push).toHaveBeenCalledWith("/sessoes/s1"));
  });
});
