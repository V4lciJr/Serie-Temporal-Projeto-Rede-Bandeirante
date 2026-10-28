# Supply Chain Forecasting — Rede Bandeirante

Sistema de sugestão de pedido de compra para o centro de distribuição de uma rede de 144 supermercados, construído sobre previsão de demanda em séries temporais e conduzido pelas 6 fases do CRISP-DM.

A previsão é insumo, não produto final: o que vai para a tela do comprador é a sugestão de pedido, montada de forma aberta (demanda prevista + estoque de segurança − estoque no CD).

## O problema

- A cada 14 dias o comprador decide, para cerca de 650 itens, quantas unidades pedir ao fornecedor.
- Processo atual: média das últimas 4 semanas de venda, ajustada no olho para promoções.
- Lead time de 14 dias + ciclo de revisão de 14 dias → **horizonte de previsão de 28 dias**.
- Custo assimétrico do erro: faltar uma unidade custa ~30% do preço (margem perdida), sobrar custa ~2% (carrego). Faltar é 15× mais caro → nível de serviço crítico de 30 / (30 + 2) = **93,75%**.

## Critério de sucesso

O projeto só é aprovado se, na avaliação, cumprir os três ao mesmo tempo:

1. WMAPE menor que o da média das últimas 4 semanas.
2. Viés próximo de zero.
3. **Custo total em R$ menor que o do processo atual**, simulando ruptura e excesso — critério eliminatório.

Métricas: `WMAPE = Σ|real − previsto| / Σreal` e `BIAS = Σ(previsto − real) / Σreal` (positivo = sobra, negativo = falta).

## Dados

| Base | Conteúdo | Uso |
|---|---|---|
| `demanda.csv` | 30 produtos × dia, 02/01/2017 a 31/10/2019 (30.849 linhas) | Base do projeto |
| `demanda_por_loja.csv` | P0131 × 144 lojas × dia (130.843 linhas) | Usada só na Fase 2 para decidir o grão |

Os arquivos vêm com separador `;` e datas `dd/mm/aaaa`; a leitura está em `src/dados.py`.

## Andamento

| Fase | Status | Principais resultados |
|---|---|---|
| 1. Entendimento do Negócio | concluída | Horizonte de 28 dias, métricas WMAPE e BIAS, critério de sucesso |
| 2. Entendimento dos Dados | concluída | Grão produto × dia na rede; P0131 com tendência forte (Ft 0,82) e ciclo semanal (Fs 0,37); promoção eleva a venda; P0438, P0051 e P0079 descontinuados |
| 3. Preparação dos Dados | em andamento | Painel com 27 produtos; P0131 separado em treino (02/01/2017–03/10/2019, 1.005 dias) e teste (04/10–31/10/2019, 28 dias) |
| 4. Modelagem | — | |
| 5. Avaliação | — | |
| 6. Deploy | — | |

Todas as decisões, com a evidência de cada uma, estão em [`relatorios/decisoes.md`](relatorios/decisoes.md).

## Regras de integridade temporal

1. Treino é sempre passado e teste sempre futuro; nada é embaralhado. O teste são os últimos 28 dias.
2. Toda feature precisa existir 28 dias antes do dia previsto: nenhum lag menor que 28, nenhuma janela móvel terminando depois de t − 28. Exceção: o calendário promocional, fechado 6 a 8 semanas antes.

## Estrutura

```
dados/brutos/          bases originais (não versionadas)
dados/processados/     bases geradas pelos notebooks (não versionadas)
notebooks/             um notebook por fase do CRISP-DM
  02_entendimento_dados.ipynb
  03_preparacao_dados.ipynb
src/                   funções reutilizáveis que vão para o deploy
  dados.py             leitura das bases
  preparacao.py        H, filtro de descontinuados, série por produto, corte treino/teste
modelos/               artefatos treinados
relatorios/
  decisoes.md          registro de decisões e limitações
  figuras/             gráficos gerados
```

## Como rodar

```
pip install -r requirements.txt
```

Coloque `demanda.csv` e `demanda_por_loja.csv` em `dados/brutos/` e execute os notebooks em ordem, a partir da pasta `notebooks/`.

## Limitações conhecidas

- `unidades` é venda observada: em dia de ruptura fica censurada e subestima a demanda.
- `estoque_total` é o saldo de fim de dia somado nas lojas, não o estoque do CD; o saldo do CD entra como informação externa no pedido.
- `pct_lojas_promo` registra a promoção realizada, não o calendário planejado que o modelo receberá em produção.
