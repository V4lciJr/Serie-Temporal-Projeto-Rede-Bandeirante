import numpy as np
import pandas as pd

from src.metricas import wmape
from src.preparacao import H


def gerar_origens(serie, n_origens=12, passo=14, horizonte=H):
    ultima = serie.index.max() - pd.Timedelta(days=horizonte)
    return [ultima - pd.Timedelta(days=passo * i) for i in range(n_origens - 1, -1, -1)]


def rodar_backtest(serie, modelos, origens, horizonte=H):
    linhas = []
    for numero, origem in enumerate(origens, start=1):
        treino = serie.loc[:origem]
        futuro = serie.loc[origem + pd.Timedelta(days=1): origem + pd.Timedelta(days=horizonte)]
        real = futuro["unidades"]
        for nome, prever in modelos.items():
            previsto = np.clip(prever(treino, futuro), 0, None)
            linhas.append({
                "origem_n": numero,
                "origem": origem,
                "inicio_teste": futuro.index.min(),
                "fim_teste": futuro.index.max(),
                "modelo": nome,
                "wmape": wmape(real, previsto),
                "real_total": real.sum(),
                "previsto_total": previsto.sum(),
                "erro_unidades": real.sum() - previsto.sum(),
                "dias_promo_teste": int((futuro["pct_lojas_promo"] > 0.2).sum()),
            })
    return pd.DataFrame(linhas)
