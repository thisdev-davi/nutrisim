/** @jest-environment node */
import { enviarMensagem } from "../sse";

// stream que entrega os pedacos na ordem, como o backend em sse
function responder(pedacos: string[], init: ResponseInit = {}) {
  const corpo = new ReadableStream({
    start(c) {
      pedacos.forEach((p) => c.enqueue(new TextEncoder().encode(p)));
      c.close();
    },
  });
  global.fetch = jest.fn().mockResolvedValue(new Response(corpo, init));
}

beforeAll(() => {
  const dados: Record<string, string> = { "nutrisim:token": "t" };
  Object.defineProperty(globalThis, "localStorage", {
    value: { getItem: (k: string) => dados[k] ?? null, setItem: () => {}, removeItem: () => {} },
  });
});

describe("enviarMensagem", () => {
  it("junta evento partido entre pedacos, ignora ping e manda o bearer", async () => {
    responder([": ping\n\nevent: tre", 'cho\r\ndata: {"texto":"Oi, "}\r\n\r\nevent: trecho\ndata: {"texto":"doutora"}\n\n', 'event: fim\ndata: {"mensagem_id":"7"}\n\n']);
    const trechos: string[] = [];

    await expect(enviarMensagem("s1", "ola", (t) => trechos.push(t))).resolves.toBe("7");
    expect(trechos).toEqual(["Oi, ", "doutora"]);
    expect((jest.mocked(fetch).mock.calls[0][1]!.headers as Headers).get("Authorization")).toBe("Bearer t");
  });

  it("lanca stream_interrompido se a conexao fecha sem fim", async () => {
    responder(['event: trecho\ndata: {"texto":"Oi"}\n\n']);
    await expect(enviarMensagem("s1", "ola", () => {})).rejects.toMatchObject({ codigo: "stream_interrompido" });
  });

  it("lanca o erro do evento e o erro do corpo antes do stream", async () => {
    responder(['event: erro\ndata: {"codigo":"paciente_indisponivel","mensagem":"tente de novo"}\n\n']);
    await expect(enviarMensagem("s1", "ola", () => {})).rejects.toEqual({ codigo: "paciente_indisponivel", mensagem: "tente de novo" });

    responder(['{"erro":{"codigo":"nao_autenticado","mensagem":"faca login"}}'], { status: 401 });
    await expect(enviarMensagem("s1", "ola", () => {})).rejects.toMatchObject({ codigo: "nao_autenticado" });
  });
});
