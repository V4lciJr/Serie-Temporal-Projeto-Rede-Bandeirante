import numpy as np


def wmape(real, previsto):
    real, previsto = np.asarray(real, dtype=float), np.asarray(previsto, dtype=float)
    return np.abs(real - previsto).sum() / real.sum() * 100


def vies(real, previsto):
    # positivo = previu demais (sobra); negativo = previu de menos (falta)
    real, previsto = np.asarray(real, dtype=float), np.asarray(previsto, dtype=float)
    return (previsto - real).sum() / real.sum() * 100
