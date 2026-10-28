# Registro de decisões

| # | Fase | Decisão | Evidência |
|---|------|---------|-----------|
| 1 | 1 | Horizonte de previsão de 28 dias | Lead time 14 dias + ciclo de revisão 14 dias |
| 2 | 1 | Métricas: WMAPE (tamanho) e BIAS = Σ(previsto − real)/Σreal (lado; positivo = sobra, negativo = falta) | Custo assimétrico: faltar custa 30% do preço, sobrar 2% (razão 15:1) |
| 3 | 1 | Critério de sucesso: bater a média de 4 semanas em WMAPE, viés próximo de zero e menor custo total em R$; o custo em R$ é eliminatório | Definido pelo condutor do projeto |
| 4 | 2 | Grão da previsão: produto × dia na rede, base `demanda.csv`; `demanda_por_loja.csv` sai do projeto | P0131 por loja: média 1,64 un/dia, mediana 0, 51,25% dos dias com venda zero, CV 2,70; na rede: média 208,06, 0% de zeros, CV 0,51. A compra é decidida no CD |
| 5 | 2 | Produto de referência para o desenvolvimento: P0131; generalização para os demais no final | Definido pelo condutor do projeto |
| 6 | 2 | Na Fase 3, remover do painel os produtos descontinuados: **P0438, P0051, P0079** (razão < 0,6) | Razão venda média últimos 90 dias / média de 455 a 90 dias atrás: P0438 0,000; P0051 0,108; P0079 0,137. Próxima menor razão: P0590 0,807. As três séries caem e ficam no chão até o fim da base |
| 7 | 3 | Regra 1 — separação temporal: treino é sempre passado, teste sempre futuro; sem shuffle, sem random_state, sem k-fold embaralhado. Teste = últimos 28 dias da série | O teste encena o horizonte da decisão (28 dias) com dados conhecidos |
| 8 | 3 | Regra 2 — toda feature precisa existir 28 dias antes do dia previsto: nenhum lag < 28, nenhuma janela móvel que termine depois de t − 28. Exceção: informação planejada antes da decisão (calendário promocional) | Uma única decisão (o pedido) cobre os 28 dias seguintes |

## Fechamento da Fase 2 — achados e decisões

| # | Achado | Decisão |
|---|--------|---------|
| 1 | Grão loja × dia é intermitente: P0131 vende 1,64 un/dia por loja, mediana 0, 51,25% dos dias com venda zero (CV 2,70). Na rede: 208,06 un/dia, 0% de zeros (CV 0,51) | Prever no grão produto × dia na rede, com `demanda.csv`; `demanda_por_loja.csv` sai do projeto |
| 2 | STL robusta (período 7) do P0131: força da tendência 0,82 e da sazonalidade semanal 0,37; fim de semana vende 1,32× o dia útil | Modelos candidatos precisam tratar tendência e sazonalidade ao mesmo tempo, com período sazonal 7; baselines (média 4 semanas e naive sazonal) ficam só como régua de comparação |
| 3 | P0438, P0051 e P0079 em descontinuação: razão 90d / (455–90d) de 0,000; 0,108; 0,137, com séries que caem e ficam no chão | Filtro de ciclo de vida na Fase 3: os três saem do painel |
| 4 | Promoção (> 20% das lojas) multiplica a venda do P0131 por 1,48 (1,15 descontando a tendência), explica 10 dos 15 maiores resíduos da STL e é fechada 6–8 semanas antes, ou seja, já é conhecida no momento da decisão | `pct_lojas_promo` entra como variável exógena na Fase 4 |
| 5 | `unidades` é venda observada, censurada em dia de ruptura; `estoque_total` é saldo de fim de dia somado nas lojas, não o estoque do CD | Nenhuma ação agora; fica registrado como limitação para a Fase 6 |

## Limitações registradas

- `unidades` é venda observada, censurada em dia de ruptura (subestima a demanda).
- `estoque_total` é saldo de fim de dia somado nas lojas, não o estoque do CD.
- `pct_lojas_promo` registra a promoção realizada, não o calendário planejado que estará disponível em produção.
