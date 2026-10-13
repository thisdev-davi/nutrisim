import { render, screen } from "@testing-library/react";
import ThemeProvider from "../ThemeProvider";

describe("ThemeProvider", () => {
  it("deve renderizar os componentes filhos corretamente", () => {
    render(
      <ThemeProvider>
        <div data-testid="filho-teste">Conteúdo do Sistema</div>
      </ThemeProvider>
    );

    const childElement = screen.getByTestId("filho-teste");
    expect(childElement).toBeInTheDocument();
    expect(childElement).toHaveTextContent("Conteúdo do Sistema");
  });
});