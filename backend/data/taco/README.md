# Base TACO

Os dados são baseados na **Tabela Brasileira de Composição de Alimentos
(TACO), 4ª edição**, do Núcleo de Estudos e Pesquisas em Alimentação
(NEPA) da Universidade Estadual de Campinas (UNICAMP).

Os CSVs deste diretório são a conversão usada pelo NutriSim para o formato
necessário ao importador. Os cabeçalhos em inglês e os identificadores
numéricos foram preservados da fonte de conversão; o importador traduz os
campos para os nomes das tabelas do backend. A conferência da origem e da
licença dos arquivos deve acompanhar a distribuição oficial da TACO.

## Valores especiais

`scripts/importar_taco.py` aplica `converter_float` aos valores numéricos:

| Valor de origem | Valor armazenado | Significado |
|---|---:|---|
| número | `float` | quantidade informada na tabela |
| `Tr` (inclusive com espaços ou maiúsculas) | `0.0` | traço, quantidade presente abaixo do limite de detecção ou quantificação |
| `NA` | `None` | dado não disponível ou não analisado |
| vazio ou apenas espaços | `None` | ausência de valor no arquivo |

Os arquivos versionados atualmente não contêm literalmente `Tr`, `NA` ou
`*`: esses valores já foram convertidos na origem dos CSVs. A regra permanece
no importador para tornar explícito o tratamento e manter a carga compatível
com novas versões da base.

`None` representa dado ausente e não deve ser interpretado pelo motor como
zero. O motor precisa decidir explicitamente como tratar campos ausentes.
