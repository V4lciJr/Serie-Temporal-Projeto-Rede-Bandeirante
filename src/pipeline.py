import numpy as np
import pandas as pd

from src.backtest import gerar_origens, rodar_backtest
from src.dados import carregar_demanda
from src.modelos import prever_sarimax_promo
from src.pedido import sugerir_pedido
from src.politica import custos_unitarios, nivel_servico_otimo
from src.preparacao import H, remover_descontinuados, serie_produto


def montar_futuro(historico, calendario_promo=None, horizonte=H):
    datas = pd.date_range(historico.index.max() + pd.Timedelta(days=1), periods=horizonte, freq="D")
    futuro = pd.DataFrame(index=datas)
    futuro.index.name = "data"
    if calendario_promo is None:
        futuro["pct_lojas_promo"] = 0.0
        return futuro, False
    calendario = calendario_promo.set_index("data")["pct_lojas_promo"]
    faltando = datas.difference(calendario.index)
    if len(faltando):
        raise ValueError(f"Calendário promocional sem {len(faltando)} datas do horizonte, a primeira é {faltando[0].date()}")
    futuro["pct_lojas_promo"] = calendario.reindex(datas).astype(float)
    if not futuro["pct_lojas_promo"].between(0, 1).all():
        raise ValueError("pct_lojas_promo precisa estar entre 0 e 1")
    return futuro, True


def executar_sugestao(produto, estoque_cd, data_decisao=None, calendario_promo=None, caminho_dados=None, n_origens=12):
    demanda = carregar_demanda(caminho_dados) if caminho_dados else carregar_demanda()
    painel = remover_descontinuados(demanda)
    if produto not in set(painel["produto"]):
        raise ValueError(f"Produto {produto} não está no painel ativo (inexistente ou descontinuado)")

    serie = serie_produto(painel, produto)
    if serie["unidades"].isna().any():
        raise ValueError(f"Série de {produto} tem {serie['unidades'].isna().sum()} dias sem registro; trate as lacunas antes")

    data_decisao = pd.Timestamp(data_decisao) if data_decisao else serie.index.max()
    historico = serie.loc[:data_decisao]
    realizado = serie.loc[data_decisao + pd.Timedelta(days=1): data_decisao + pd.Timedelta(days=H)]

    if calendario_promo is None and len(realizado) == H:
        # modo simulação: data de decisão no passado, usa a promoção registrada na base para o horizonte
        calendario_promo = realizado["pct_lojas_promo"].rename_axis("data").reset_index()
    futuro, tem_calendario = montar_futuro(historico, calendario_promo)

    # erros do backtest só com janelas que já terminaram na data da decisão
    backtest = rodar_backtest(historico, {"SARIMAX + promoção": prever_sarimax_promo}, gerar_origens(historico, n_origens=n_origens))
    nivel_servico = nivel_servico_otimo(*custos_unitarios(historico["preco_medio"].mean()))
    resultado = sugerir_pedido(historico, futuro, backtest["erro_unidades"].values, estoque_cd, nivel_servico)

    previsao_diaria = pd.DataFrame({"pct_lojas_promo": futuro["pct_lojas_promo"],
                                    "previsao_unidades": resultado.pop("previsao_diaria")}, index=futuro.index)
    resultado.update({
        "produto": produto,
        "data_decisao": data_decisao,
        "inicio_horizonte": futuro.index.min(),
        "fim_horizonte": futuro.index.max(),
        "nivel_servico": nivel_servico,
        "origens_backtest": len(backtest),
        "calendario_promo_informado": tem_calendario,
        "vendido_realizado": float(realizado["unidades"].sum()) if len(realizado) == H else np.nan,
    })
    return resultado, previsao_diaria
