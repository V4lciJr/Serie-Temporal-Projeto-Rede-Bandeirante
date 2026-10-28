from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_DEMANDA = RAIZ / "dados" / "brutos" / "demanda.csv"


def carregar_demanda(caminho=CAMINHO_DEMANDA):
    # arquivo exportado com separador ";" e data no formato dd/mm/aaaa
    df = pd.read_csv(caminho, sep=";")
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    return df.sort_values(["produto", "data"]).reset_index(drop=True)


CAMINHO_DEMANDA_LOJA = RAIZ / "dados" / "brutos" / "demanda_por_loja.csv"


def carregar_demanda_loja(caminho=CAMINHO_DEMANDA_LOJA):
    df = pd.read_csv(caminho, sep=";")
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    return df.sort_values(["loja", "data"]).reset_index(drop=True)
