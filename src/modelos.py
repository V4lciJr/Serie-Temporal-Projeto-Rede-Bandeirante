import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

ORDEM_SARIMA = (2, 1, 2)
ORDEM_SAZONAL = (1, 1, 1, 7)


def prever_naive_sazonal(treino, futuro):
    return np.tile(treino["unidades"].iloc[-7:].values, int(np.ceil(len(futuro) / 7)))[:len(futuro)]


def prever_media_4_semanas(treino, futuro):
    return np.repeat(treino["unidades"].iloc[-28:].mean(), len(futuro))


def prever_holt_winters(treino, futuro):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo = ExponentialSmoothing(treino["unidades"], trend="add", seasonal="add",
                                      seasonal_periods=7, initialization_method="estimated").fit()
    return modelo.forecast(len(futuro)).values


def prever_sarima(treino, futuro):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo = SARIMAX(treino["unidades"], order=ORDEM_SARIMA,
                         seasonal_order=ORDEM_SAZONAL).fit(disp=False, maxiter=200)
    return modelo.forecast(len(futuro)).values


def prever_sarimax_promo(treino, futuro):
    # futuro só fornece pct_lojas_promo: o calendário promocional já é conhecido na data da decisão
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo = SARIMAX(treino["unidades"], exog=treino[["pct_lojas_promo"]], order=ORDEM_SARIMA,
                         seasonal_order=ORDEM_SAZONAL).fit(disp=False, maxiter=200)
    return modelo.forecast(len(futuro), exog=futuro[["pct_lojas_promo"]]).values


MODELOS = {
    "Naive sazonal (7d)": prever_naive_sazonal,
    "Média 4 semanas (atual)": prever_media_4_semanas,
    "Holt-Winters aditivo": prever_holt_winters,
    "SARIMA (2,1,2)(1,1,1,7)": prever_sarima,
    "SARIMAX + promoção": prever_sarimax_promo,
}
