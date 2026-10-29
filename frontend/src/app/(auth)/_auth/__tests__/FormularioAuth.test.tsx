import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormularioAuth } from "../FormularioAuth";

const login = jest.fn();
const cadastro = jest.fn();
jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../../components/providers/AuthProvider", () => ({ useAuth: () => ({ login, cadastro }) }));

describe("FormularioAuth", () => {
  it("foca o primeiro campo invalido e diz quanto falta na senha", async () => {
    const user = userEvent.setup();
    render(<FormularioAuth modo="criar" />);

    await user.type(screen.getByLabelText("Nome"), "Ana");
    await user.type(screen.getByLabelText("E-mail"), "ana@");
    await user.type(screen.getByLabelText("Senha"), "abc12");
    await user.click(screen.getByRole("button", { name: "Criar conta e entrar" }));

    expect(screen.getByLabelText("E-mail")).toHaveFocus();
    expect(screen.getByText("Use pelo menos 8 caracteres. Faltam 3.")).toBeInTheDocument();
    expect(cadastro).not.toHaveBeenCalled();
  });

  it("e-mail ja cadastrado oferece entrar com ele", async () => {
    cadastro.mockRejectedValueOnce({ codigo: "email_em_uso", mensagem: "" });
    const user = userEvent.setup();
    render(<FormularioAuth modo="criar" />);

    await user.type(screen.getByLabelText("Nome"), "Ana");
    await user.type(screen.getByLabelText("E-mail"), "ana@exemplo.com");
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: "Criar conta e entrar" }));

    expect(await screen.findByRole("link", { name: "Entrar com este e-mail" })).toHaveAttribute("href", "/login?email=ana%40exemplo.com");
  });

  it("senha errada limpa a senha e mantem o e-mail", async () => {
    login.mockRejectedValueOnce({ codigo: "credenciais_invalidas", mensagem: "" });
    const user = userEvent.setup();
    render(<FormularioAuth modo="entrar" email="ana@exemplo.com" />);

    await user.type(screen.getByLabelText("Senha"), "errada");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText(/E-mail ou senha incorretos/)).toBeInTheDocument();
    expect(screen.getByLabelText("Senha")).toHaveValue("");
    expect(screen.getByLabelText("E-mail")).toHaveValue("ana@exemplo.com");
  });

  it("redirect com barra invertida nao sai do site", async () => {
    login.mockResolvedValueOnce(undefined);
    const user = userEvent.setup();
    render(<FormularioAuth modo="entrar" email="ana@exemplo.com" redirect={"/\\evil.com"} />);

    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("link", { name: "abra o NutriSim" })).toHaveAttribute("href", "/caso/novo");
  });
});
