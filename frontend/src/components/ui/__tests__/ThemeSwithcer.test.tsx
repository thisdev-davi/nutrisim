import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ThemeSwitch from "../ThemeSwitcher";

// 1. "Finge" a importação do next-themes
jest.mock("next-themes", () => ({
  useTheme: jest.fn(),
}));

// Importa o hook mockado para podermos alterar os valores dele em cada teste
import { useTheme } from "next-themes"; 

describe("ThemeSwitch", () => {
  const mockSetTheme = jest.fn(); // Cria uma função falsa para monitorar se ela foi chamada

  beforeEach(() => {
    jest.clearAllMocks(); // Limpa a memória dos testes anteriores
  });

  it("deve renderizar corretamente com o tema 'light'", () => {
    // Configuramos o mock para fingir que o tema atual é light
    (useTheme as jest.Mock).mockReturnValue({ theme: "light", setTheme: mockSetTheme });
    render(<ThemeSwitch />);

    // Verifica se o botão apareceu na tela com o texto certo
    const button = screen.getByRole("button", { name: /Trocar Tema \(light\)/i });
    expect(button).toBeInTheDocument();
  });

  it("deve alterar para o tema 'dark' ao clicar quando o tema for 'light'", async () => {

    (useTheme as jest.Mock).mockReturnValue({ theme: "light", setTheme: mockSetTheme });    
    const user = userEvent.setup(); // Prepara a simulação de usuário

    render(<ThemeSwitch />);
    const button = screen.getByRole("button");

    // Simula o clique do usuário
    await user.click(button);

    // Garante que a função foi chamada passando "dark"
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
    expect(mockSetTheme).toHaveBeenCalledTimes(1);
  });

  it("deve alterar para o tema 'light' ao clicar quando o tema for 'dark'", async () => {
    (useTheme as jest.Mock).mockReturnValue({ theme: "dark", setTheme: mockSetTheme });    
    const user = userEvent.setup();

    render(<ThemeSwitch />);
    const button = screen.getByRole("button");

    await user.click(button);

    // Garante que a função foi chamada passando "light"
    expect(mockSetTheme).toHaveBeenCalledWith("light");
  });
});