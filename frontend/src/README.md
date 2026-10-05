# frontend

Aplicação web em Next.js (React) com Tailwind CSS, pensada primeiro para o celular e adaptada ao computador.

**Responsável:** Pedro Augusto.

> Ainda não há código. O projeto será criado no card NS-009.
>
> **Atenção:** o `create-next-app` exige uma pasta vazia. Antes de rodá-lo, tire este README da pasta e depois incorpore o conteúdo ao README gerado.

## Estrutura prevista

```text
frontend/
├── src/
│   ├── app/                    rotas (App Router)
│   │   ├── page.tsx            início
│   │   ├── entrar/             login e cadastro (RF01)                           NS-036
│   │   ├── casos/novo/         escolha de perfil e dificuldade (RF02)            NS-021
│   │   ├── sessoes/[id]/
│   │   │   ├── anamnese/       chat em tempo real com o paciente (RF04)         NS-022
│   │   │   ├── plano/          montagem do plano com busca na TACO (RF05, RF06) NS-042
│   │   │   ├── cenarios/       ideal × realista, gráficos de peso e adequação   NS-048
│   │   │   ├── retorno/        consulta de retorno (RF09)                        NS-052
│   │   │   └── feedback/       resultado da rubrica (RF10)                       NS-052
│   │   └── historico/          sessões anteriores e evolução (RF11)              NS-054
│   ├── components/             chat, busca de alimentos, gráficos, navegação entre etapas
│   └── lib/                    cliente da API tipado a partir do contrato (docs/api.md)
└── e2e/                        testes Playwright em celular (360 px) e desktop   NS-060
```

As rotas são uma proposta e podem mudar com os wireframes (NS-010) e o contrato da API (NS-007).

## Requisitos que valem para toda tela

- **Responsividade:** tem que funcionar a partir de 360 px de largura.
- **Acessibilidade:** contraste adequado, navegação por teclado, rótulos para leitores de tela.
- **Desempenho percebido:** a resposta do paciente aparece em streaming, e toda espera mostra um estado de carregamento.
- **Sem IA no navegador:** o frontend só conversa com o backend e nunca chama o provedor de LLM.
- **Projeções com aviso:** gráficos de peso e adequação sempre exibem a limitação do modelo.
