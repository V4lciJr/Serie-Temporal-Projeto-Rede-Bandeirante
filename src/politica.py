import numpy as np

PCT_CUSTO_FALTA = 0.30
PCT_CUSTO_SOBRA = 0.02


def custos_unitarios(preco_medio, pct_falta=PCT_CUSTO_FALTA, pct_sobra=PCT_CUSTO_SOBRA):
    return pct_falta * preco_medio, pct_sobra * preco_medio


def nivel_servico_otimo(custo_falta, custo_sobra):
    return custo_falta / (custo_falta + custo_sobra)


def estoque_seguranca_empirico(erros_periodo, nivel_servico):
    # erros_periodo = realizado − previsto por origem; o quantil é a folga que cobre esse nível de serviço
    return float(np.quantile(np.asarray(erros_periodo, dtype=float), nivel_servico))


def simular_politica(backtest_modelo, nivel_servico, custo_falta, custo_sobra):
    # backtest_modelo: uma linha por origem com real_total, previsto_total e erro_unidades (realizado − previsto)
    estoque_seg = estoque_seguranca_empirico(backtest_modelo["erro_unidades"], nivel_servico)
    pedido = backtest_modelo["previsto_total"] + estoque_seg
    falta = (backtest_modelo["real_total"] - pedido).clip(lower=0)
    sobra = (pedido - backtest_modelo["real_total"]).clip(lower=0)
    custo = falta * custo_falta + sobra * custo_sobra
    return {
        "estoque_seguranca_un": estoque_seg,
        "custo_medio_periodo_R$": custo.mean(),
        "falta_media_un": falta.mean(),
        "sobra_media_un": sobra.mean(),
        "custo_falta_medio_R$": (falta * custo_falta).mean(),
        "custo_sobra_medio_R$": (sobra * custo_sobra).mean(),
        "origens_com_falta_%": (falta > 0).mean() * 100,
    }
