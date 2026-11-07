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
| 9 | 3 | Painel sem descontinuados: 27 produtos, 27.883 linhas, sem nulos em `unidades`. P0131: treino 02/01/2017–03/10/2019 (1.005 dias), teste 04/10–31/10/2019 (28 dias) | Aplicação das decisões 6 e 7 |
| 10 | 4 | Avaliação única para todos os modelos: WMAPE e viés com clip em zero na previsão | Função `avaliar` sobre as mesmas 28 datas de teste |
| 11 | 4 | Escada de modelos: naive sazonal → média 4 semanas → Holt-Winters aditivo (período 7) → SARIMA (2,1,2)(1,1,1,7) → SARIMAX + `pct_lojas_promo` | Teste único: WMAPE 10,17 / 17,18 / 9,30 / 8,43 / 8,44%; coeficiente da promoção +65,3 un/dia (IC 95% 51,3–79,4) |
| 12 | 5 | Avaliação por backtest com origem móvel: 12 origens, passo de 14 dias, 28 dias de teste cada | WMAPE médio: Holt-Winters 15,36; SARIMAX 15,50; naive 16,15; SARIMA 17,51; média 4 semanas 22,05%. Sem a pior origem (origem 1, pós-promoção de abril/2019): SARIMAX 11,80; Holt-Winters 12,82% |
| 13 | 5 | Nível de serviço 93,75% (Cu / (Cu + Co)) e estoque de segurança pelo quantil empírico dos erros do backtest, sem supor erro normal | Cu R$ 0,7761 e Co R$ 0,0517 no preço médio de R$ 2,59; erros com cauda pesada (pior origem muito acima das demais) |
| 14 | 5 | Critério 3: só o SARIMAX + promoção reduz o custo em R$ contra o processo atual | Custo por período: SARIMAX R$ 107,99; média 4 semanas R$ 147,11; Holt-Winters R$ 160,15. SARIMAX: −26,6%, estoque de segurança 786 un contra 2.112, economia de R$ 508,57/ano no P0131 |
| 15 | 6 | Pedido em conta aberta: demanda prevista + estoque de segurança − estoque no CD = pedido; estoque do CD informado na execução (3.000 un no cenário de teste) | Requisito do comprador: entender de onde sai o número. Cenário 6.1: previsão 8.238 un contra 8.158 vendidas (+0,98%); pedido de 6.024 un |
| 16 | 6 | Deploy como script `sugerir_pedido.py` que retreina o SARIMAX e recalcula o estoque de segurança a cada execução, só com janelas encerradas até a data da decisão | O SARIMAX depende do histórico recente; um modelo estático envelhece |

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
- O estoque de segurança da simulação foi calculado com os mesmos 12 erros em que é avaliado (resultado levemente otimista para todos os modelos).
- As janelas do backtest se sobrepõem (28 dias com passo de 14): as 12 origens não são independentes.
- Estoque de segurança instável com 12 origens: na decisão simulada em 03/10/2019 (origens de 04/04 a 05/09) ele é 1.603 un; com as origens da Fase 5 (02/05 a 03/10) é 786 un. A diferença é a janela da promoção de abril/2019.
