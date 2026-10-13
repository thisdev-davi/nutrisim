import { render, screen } from "@testing-library/react";
import QueryProvider from "../QueryProvider";

describe("QueryProvider", () => {
  it("deve envolver a aplicação e renderizar os filhos", () => {
    render(
      <QueryProvider>
        <h1>Painel do Usuário</h1>
      </QueryProvider>
    );

    const heading = screen.getByRole("heading", { name: "Painel do Usuário" });
    expect(heading).toBeInTheDocument();
  });
});