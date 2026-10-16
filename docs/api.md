# Contrato da API

O contrato vivo é o OpenAPI gerado pelo código: rode o backend e abra `http://localhost:8000/docs`. Lá ficam as rotas, os corpos e as respostas de cada endpoint (resumo no [`backend/README.md`](../backend/README.md#contrato-da-api)). Este arquivo cobre o que o OpenAPI não mostra: **como o frontend consome o stream do paciente** e **como exibe cada erro**.

Card: NS-007. Por enquanto só existem as etapas 1 (caso) e 2 (anamnese). As etapas 3 a 5 entram aqui quando forem construídas.

## Regras gerais

- Todas as rotas ficam sob `/api`. A URL do backend vem de variável de ambiente. Como as chamadas rodam no navegador, no Next.js ela precisa do prefixo `NEXT_PUBLIC_` (hoje o `.env.example` do front tem `BACK_END_API`).
- **A ficha oculta nunca sai do backend.** O front só recebe o que o estudante pode ver do paciente (`nome`, `idade`, `queixa_principal`) e o histórico da conversa.
- **Autenticação:** `Authorization: Bearer <token>` está declarado, mas só passa a ser exigido na NS-035. Até lá, o front pode mandar o header ou não.
- **Mock:** até a NS-019 e a NS-020, as rotas devolvem dados fixos. A única sessão que existe é `mock`. O `POST /api/sessoes` sempre devolve essa sessão.

## Fluxo das etapas 1 e 2

1. `GET /api/perfis` monta a tela de seleção (NS-021).
2. `POST /api/sessoes` cria o caso. Guarde o `id` da sessão na URL da página (por exemplo, `/sessoes/{id}`) para poder retomar.
3. Ao abrir ou recarregar a anamnese (NS-022), `GET /api/sessoes/{id}` devolve o paciente e as `mensagens` já trocadas.
4. Cada pergunta é um `POST /api/sessoes/{id}/mensagens`, e a fala do paciente chega em streaming.
5. `POST /api/sessoes/{id}/anamnese/encerrar` devolve `{"etapa": "plano"}`.

O histórico fica no backend. O front não precisa reenviá-lo a cada turno: ele manda só a pergunta nova.

## Como consumir o stream do paciente

A rota de mensagens é `POST` com resposta em Server-Sent Events. O `EventSource` do navegador só faz `GET`, então a leitura é feita com `fetch` e `ReadableStream`, sem biblioteca:

```ts
type Erro = { codigo: string; mensagem: string };

export async function enviarMensagem(
  sessaoId: string,
  texto: string,
  aoTrecho: (texto: string) => void,
): Promise<string> {
  const resp = await fetch(`${API_URL}/api/sessoes/${sessaoId}/mensagens`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  // 404 e 422 chegam antes de o stream abrir, como JSON comum
  if (!resp.ok) throw ((await resp.json()) as { erro: Erro }).erro;

  const leitor = resp.body!.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await leitor.read();
    if (done) throw { codigo: "stream_interrompido", mensagem: "A conexão caiu. Tente de novo." };
    buffer += value;
    const blocos = buffer.split("\n\n");
    buffer = blocos.pop()!; // bloco incompleto fica para a próxima leitura
    for (const bloco of blocos) {
      const evento = bloco.match(/^event: (.*)$/m)?.[1];
      const dados = bloco.match(/^data: (.*)$/m)?.[1];
      if (!dados) continue; // ": ping" de keep-alive
      if (evento === "trecho") aoTrecho(JSON.parse(dados).texto);
      if (evento === "fim") return JSON.parse(dados).mensagem_id;
      if (evento === "erro") throw JSON.parse(dados) as Erro;
    }
  }
}
```

Eventos, nesta ordem:

| Evento | `data` | O que o front faz |
|---|---|---|
| `trecho` (vários) | `{"texto"}` | concatena o texto na bolha do paciente |
| `fim` | `{"mensagem_id"}` | a fala está completa e salva no histórico |
| `erro` | `{"codigo", "mensagem"}` | descarta o texto parcial e mostra o erro |

O stream termina sempre em `fim` ou em `erro`. Se a conexão fechar sem nenhum dos dois, trate como erro (`stream_interrompido` no exemplo). Linhas `: ping` são keep-alive enviados quando o paciente demora e devem ser ignoradas.

Acessibilidade (NS-022): anuncie a fala na região `aria-live` só no `fim`, com o texto completo. Anunciar cada `trecho` faz o leitor de tela ler palavra por palavra.

## Como exibir cada erro

Toda resposta de erro, fora do stream, tem o formato `{"erro": {"codigo", "mensagem"}}`. Dentro do stream, o evento `erro` traz o mesmo `{"codigo", "mensagem"}`. O front decide o que fazer pelo `codigo` e mostra a `mensagem` ao estudante.

| `codigo` | Status | Quando | O que o front exibe |
|---|---|---|---|
| `sessao_nao_encontrada` | 404 | o id da URL não existe | a mensagem e um botão para começar um novo caso |
| `perfil_invalido` | 422 | perfil escolhido não existe mais | a mensagem e recarrega a lista de perfis |
| `dados_invalidos` | 422 | corpo fora do contrato (por exemplo, mensagem vazia ou acima de 2.000 caracteres) | bloqueie no formulário antes de enviar. Se chegar mesmo assim, é bug do front |
| `erro_interno` | 500 | falha inesperada no backend | a mensagem e um botão "Tentar de novo" |
| `http_<status>` | outro | rota ou método inexistente | é bug do front: mensagem genérica |
| `stream_interrompido` | – | gerado pelo front quando a conexão cai | a mensagem e "Tentar de novo", reenviando a mesma pergunta |

Os códigos que o paciente com LLM vai emitir no evento `erro` (NS-020 e NS-070) entram nesta tabela quando esses cards forem feitos.
