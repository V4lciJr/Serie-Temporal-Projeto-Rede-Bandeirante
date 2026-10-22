# Supply Chain Forecasting — Rede Bandeirante

Sistema de sugestão de pedido de compra para o CD da Rede Bandeirante, construído sobre previsão de demanda em séries temporais e seguindo o CRISP-DM.

## Estrutura

```
dados/brutos/        bases originais (não versionadas)
dados/processados/   bases geradas pelo pipeline
notebooks/           um notebook por fase do CRISP-DM
src/                 funções reutilizáveis (preparação, features, modelos, inferência)
modelos/             artefatos treinados
relatorios/figuras/  gráficos gerados
```

## Como rodar

```
pip install -r requirements.txt
```

As bases `demanda.csv` e `demanda_por_loja.csv` devem estar em `dados/brutos/`.
