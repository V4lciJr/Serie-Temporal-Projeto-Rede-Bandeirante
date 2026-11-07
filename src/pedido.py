import numpy as np

from src.modelos import prever_sarimax_promo
from src.politica import estoque_seguranca_empirico


def sugerir_pedido(historico, futuro, erros_backtest, estoque_cd, nivel_servico, prever=prever_sarimax_promo):
    # futuro: as datas do horizonte com pct_lojas_promo planejado; a venda futura não é usada
    previsao_diaria = np.clip(prever(historico, futuro), 0, None)
    demanda_prevista = float(previsao_diaria.sum())
    estoque_seg = estoque_seguranca_empirico(erros_backtest, nivel_servico)
    necessidade = demanda_prevista + estoque_seg
    return {
        "demanda_prevista": demanda_prevista,
        "estoque_seguranca": estoque_seg,
        "necessidade_bruta": necessidade,
        "estoque_cd": float(estoque_cd),
        "pedido": max(necessidade - estoque_cd, 0.0),
        "previsao_diaria": previsao_diaria,
    }
