import { act, render } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "../AuthProvider";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));

describe("AuthProvider", () => {
  it("logout apaga o cache para a proxima conta nao ver as sessoes da anterior", () => {
    const client = new QueryClient();
    client.setQueryData(["sessoes"], [{ id: "s1" }]);
    let auth!: ReturnType<typeof useAuth>;
    function Espiao() {
      auth = useAuth();
      return null;
    }
    render(
      <QueryClientProvider client={client}>
        <AuthProvider>
          <Espiao />
        </AuthProvider>
      </QueryClientProvider>
    );

    act(() => auth.logout());

    expect(client.getQueryData(["sessoes"])).toBeUndefined();
  });
});
