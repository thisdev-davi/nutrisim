export interface SSEMessage {
  event: string;
  data: string;
}

interface FetchSSEOptions extends RequestInit {
  onMessage: (msg: SSEMessage) => void;
  onError?: (err: unknown) => void;
}

export async function fetchSSE(url: string, options: FetchSSEOptions) {
  const { onMessage, onError, ...fetchOptions } = options;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: {
        ...fetchOptions.headers,
        Accept: "text/event-stream",
      },
    });

    if (!response.ok) {
      throw new Error(`Falha na requisição: ${response.status} ${response.statusText}`);
    }
    if (!response.body) {
      throw new Error("O corpo da resposta está vazio.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Decodifica os bytes recebidos e junta ao buffer
      buffer += decoder.decode(value, { stream: true });

      // O protocolo SSE separa as mensagens por "\n\n"
      let limite = buffer.indexOf("\n\n");
      while (limite !== -1) {
        const bloco = buffer.slice(0, limite);
        buffer = buffer.slice(limite + 2);

        let eventType = "message";
        let eventData = "";

        // Lê as linhas do bloco para extrair 'event:' e 'data:'
        const linhas = bloco.split("\n");
        for (const linha of linhas) {
          if (linha.startsWith("event:")) {
            eventType = linha.replace("event:", "").trim();
          } else if (linha.startsWith("data:")) {
            eventData = linha.replace("data:", "").trim();
          }
        }

        if (eventData) {
          onMessage({ event: eventType, data: eventData });
        }

        limite = buffer.indexOf("\n\n");
      }
    }
  } catch (error) {
    if (onError) onError(error);
    else throw error;
  }
}