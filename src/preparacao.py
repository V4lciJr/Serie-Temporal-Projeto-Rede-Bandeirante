import pandas as pd

H = 28
PRODUTOS_DESCONTINUADOS = ["P0438", "P0051", "P0079"]


def remover_descontinuados(demanda, produtos=PRODUTOS_DESCONTINUADOS):
    return demanda[~demanda["produto"].isin(produtos)].reset_index(drop=True)


def serie_produto(demanda, produto):
    return (demanda.loc[demanda["produto"] == produto]
            .set_index("data")
            .drop(columns="produto")
            .asfreq("D"))


def ponto_de_corte(serie, horizonte=H):
    return serie.index.max() - pd.Timedelta(days=horizonte)


def separar_treino_teste(serie, horizonte=H):
    corte = ponto_de_corte(serie, horizonte)
    return serie.loc[:corte], serie.loc[corte + pd.Timedelta(days=1):]
