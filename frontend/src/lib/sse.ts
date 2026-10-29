import { requisitar, type Erro } from "@/lib/api";

// le o stream do paciente (docs/api.md); resolve com o id da fala ou lanca o Erro do contrato
export async function enviarMensagem(
  sessaoId: string,
  texto: string,
  aoTrecho: (texto: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  const resp = await requisitar(`/sessoes/${sessaoId}/mensagens`, {
    method: "POST",
    headers: { Accept: "text/event-stream" },
    body: JSON.stringify({ texto }),
    signal,
  });
  const leitor = resp.body!.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await leitor.read();
    if (done) throw { codigo: "stream_interrompido", mensagem: "A conexão caiu. Tente de novo." } satisfies Erro;
    buffer += value.replace(/\r/g, "");
    const blocos = buffer.split("\n\n");
    buffer = blocos.pop()!; // bloco incompleto fica para a proxima leitura
    for (const bloco of blocos) {
      const evento = bloco.match(/^event: ?(.*)$/m)?.[1];
      const dados = bloco.match(/^data: ?(.*)$/m)?.[1];
      if (!dados) continue; // ": ping" de keep-alive
      if (evento === "trecho") aoTrecho(JSON.parse(dados).texto);
      if (evento === "fim") return JSON.parse(dados).mensagem_id;
      if (evento === "erro") throw JSON.parse(dados) as Erro;
    }
  }
}
