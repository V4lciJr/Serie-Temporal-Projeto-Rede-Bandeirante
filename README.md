# Supply Chain Forecasting — Rede Bandeirante

Sistema de sugestão de pedido de compra para o centro de distribuição de uma rede de 144 supermercados, construído sobre previsão de demanda em séries temporais e conduzido pelas 6 fases do CRISP-DM.

A previsão é insumo, não produto final: o que vai para a tela do comprador é a sugestão de pedido, montada de forma aberta (demanda prevista + estoque de segurança − estoque no CD).

## O problema

- A cada 14 dias o comprador decide, para cerca de 650 itens, quantas unidades pedir ao fornecedor.
- Processo atual: média das últimas 4 semanas de venda, ajustada no olho para promoções.
- Lead time de 14 dias + ciclo de revisão de 14 dias → **horizonte de previsão de 28 dias**.
- Custo assimétrico do erro: faltar uma unidade custa ~30% do preço (margem perdida), sobrar custa ~2% (carrego). Faltar é 15× mais caro → nível de serviço ótimo de 30 / (30 + 2) = **93,75%**.

## Critério de sucesso

O projeto só é aprovado se, na avaliação, cumprir os três ao mesmo tempo:

1. WMAPE menor que o da média das últimas 4 semanas.
2. Viés próximo de zero.
3. **Custo total em R$ menor que o do processo atual**, simulando ruptura e excesso — critério eliminatório.

Métricas: `WMAPE = Σ|real − previsto| / Σreal` e `BIAS = Σ(previsto − real) / Σreal` (positivo = sobra, negativo = falta).

## Resultados (produto de referência P0131)

Backtest com origem móvel: 12 origens espaçadas de 14 dias, cada uma prevendo os 28 dias seguintes.

| Modelo | WMAPE médio | WMAPE sem a pior origem | Estoque de segurança | Custo por período | vs. processo atual |
|---|---|---|---|---|---|
| **SARIMAX (2,1,2)(1,1,1,7) + promoção** | 15,50% | **11,80%** | **786 un** | **R$ 107,99** | **−26,6%** |
| Holt-Winters aditivo | **15,36%** | 12,82% | 1.484 un | R$ 160,15 | +8,9% |
| SARIMA (2,1,2)(1,1,1,7) | 17,51% | 12,85% | — | — | — |
| Naive sazonal (7 dias) | 16,15% | 13,98% | — | — | — |
| Média 4 semanas (processo atual) | 22,05% | 19,09% | 2.112 un | R$ 147,11 | — |

- Todos os modelos batem o processo atual em WMAPE (critério 1).
- O Holt-Winters tem o menor WMAPE médio, mas erra para baixo nas janelas de promoção, precisa de mais folga e fica **mais caro** que o processo atual.
- Só o SARIMAX com promoção cumpre o critério 3: economia de R$ 508,57/ano neste único produto (preço médio R$ 2,59), com 1.326 unidades a menos de estoque de segurança.

## Andamento

| Fase | Status | Principais resultados |
|---|---|---|
| 1. Entendimento do Negócio | concluída | Horizonte de 28 dias, métricas WMAPE e BIAS, critério de sucesso |
| 2. Entendimento dos Dados | concluída | Grão produto × dia na rede; P0131 com tendência forte (Ft 0,82) e ciclo semanal (Fs 0,37); promoção eleva a venda; P0438, P0051 e P0079 descontinuados |
| 3. Preparação dos Dados | concluída | Painel com 27 produtos; P0131 em treino (02/01/2017–03/10/2019) e teste (04/10–31/10/2019) |
| 4. Modelagem | concluída | Escada naive → média 4 semanas → Holt-Winters → SARIMA → SARIMAX; promoção = +65 un/dia com a rede inteira em promoção |
| 5. Avaliação | concluída | Backtest de 12 origens, estoque de segurança empírico e simulação financeira (tabela acima) |
| 6. Deploy | — | |

Todas as decisões, com a evidência de cada uma, estão em [`relatorios/decisoes.md`](relatorios/decisoes.md).

## Regras de integridade temporal

1. Treino é sempre passado e teste sempre futuro; nada é embaralhado. O teste são os últimos 28 dias.
2. Toda feature precisa existir 28 dias antes do dia previsto: nenhum lag menor que 28, nenhuma janela móvel terminando depois de t − 28. Exceção: o calendário promocional, fechado 6 a 8 semanas antes.

## Estrutura

```
dados/brutos/          bases originais (não versionadas)
dados/processados/     bases geradas pelos notebooks (não versionadas)
notebooks/
  02_entendimento_dados.ipynb   diagnóstico, grão, tendência, sazonalidade, STL, ciclo de vida, promoção
  03_preparacao_dados.ipynb     filtro de descontinuados e separação treino/teste
  04_modelagem.ipynb            escada de modelos no teste único
  05_avaliacao.ipynb            backtest, nível de serviço, estoque de segurança e custo
src/                   funções reutilizáveis que vão para o deploy
  dados.py             leitura das bases (separador ";", datas dd/mm/aaaa)
  preparacao.py        H = 28, filtro de descontinuados, série por produto, corte treino/teste
  metricas.py          wmape e vies
  modelos.py           os 5 modelos da escada com interface comum prever(treino, futuro)
  backtest.py          origens móveis e execução do backtest
  politica.py          custos, nível de serviço, estoque de segurança empírico e simulação da política
modelos/               artefatos treinados
relatorios/
  decisoes.md          registro de decisões e limitações
  figuras/             gráficos gerados pelos notebooks
```

## Como rodar

```
pip install -r requirements.txt
```

Coloque `demanda.csv` e `demanda_por_loja.csv` em `dados/brutos/` e execute os notebooks em ordem, a partir da pasta `notebooks/`. O backtest da Fase 5 leva cerca de 1 minuto e é salvo em `dados/processados/backtest_P0131.csv`; se o arquivo existir, o notebook o reaproveita.

## Limitações conhecidas

- `unidades` é venda observada: em dia de ruptura fica censurada e subestima a demanda.
- `estoque_total` é o saldo de fim de dia somado nas lojas, não o estoque do CD; o saldo do CD entra como informação externa no pedido.
- `pct_lojas_promo` registra a promoção realizada, não o calendário planejado que o modelo receberá em produção.
- O estoque de segurança é estimado com 12 origens que se sobrepõem; os percentuais de falta andam de 8,33 em 8,33 pontos e o resultado é levemente otimista.
- Os resultados são do P0131; a generalização para os demais produtos ainda não foi testada.
