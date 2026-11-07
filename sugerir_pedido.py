import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.pipeline import executar_sugestao

RAIZ = Path(__file__).resolve().parent


def ler_calendario(caminho):
    calendario = pd.read_csv(caminho, sep=None, engine="python")
    calendario["data"] = pd.to_datetime(calendario["data"], dayfirst=True)
    return calendario[["data", "pct_lojas_promo"]]


def imprimir(r):
    print(f"\nSUGESTÃO DE PEDIDO — {r['produto']} | decisão em {r['data_decisao']:%d/%m/%Y} | "
          f"cobre {r['inicio_horizonte']:%d/%m} a {r['fim_horizonte']:%d/%m/%Y}")
    print("-" * 78)
    print(f"   Demanda prevista (28 dias, SARIMAX + promoção)   {r['demanda_prevista']:>10,.2f} un")
    print(f" + Estoque de segurança (nível de serviço {r['nivel_servico']:.2%})  {r['estoque_seguranca']:>10,.2f} un")
    print(f" = Necessidade bruta                                 {r['necessidade_bruta']:>10,.2f} un")
    print(f" − Estoque disponível no CD                          {r['estoque_cd']:>10,.2f} un")
    print(f" = PEDIDO AO FORNECEDOR                              {r['pedido']:>10,.2f} un  (≈ {np.ceil(r['pedido']):,.0f})")
    print("-" * 78)
    print(f"Estoque de segurança estimado com {r['origens_backtest']} origens de backtest.")
    if not r["calendario_promo_informado"]:
        print("ATENÇÃO: nenhum calendário promocional informado; o horizonte foi tratado como sem promoção.")
    if not np.isnan(r["vendido_realizado"]):
        sobra = r["estoque_cd"] + r["pedido"] - r["vendido_realizado"]
        print(f"Simulação: vendido de fato {r['vendido_realizado']:,.0f} un | "
              f"{'sobra' if sobra >= 0 else 'falta'} de {abs(sobra):,.0f} un no fim do período")


def main():
    parser = argparse.ArgumentParser(description="Sugestão de pedido de compra para o CD (horizonte de 28 dias)")
    parser.add_argument("--produto", required=True, help="código do SKU, ex.: P0131")
    parser.add_argument("--estoque-cd", type=float, required=True, help="saldo atual do produto no CD, em unidades")
    parser.add_argument("--calendario", help="CSV com colunas data e pct_lojas_promo para os 28 dias do horizonte")
    parser.add_argument("--data-decisao", help="AAAA-MM-DD; padrão: última data da base. Uma data passada simula a decisão")
    parser.add_argument("--dados", help="caminho do demanda.csv; padrão: dados/brutos/demanda.csv")
    parser.add_argument("--origens", type=int, default=12, help="origens do backtest para o estoque de segurança (padrão 12)")
    args = parser.parse_args()

    calendario = ler_calendario(args.calendario) if args.calendario else None
    resultado, previsao_diaria = executar_sugestao(args.produto, args.estoque_cd, args.data_decisao, calendario, args.dados, args.origens)
    imprimir(resultado)

    pasta = RAIZ / "saidas"
    pasta.mkdir(exist_ok=True)
    sufixo = f"{resultado['produto']}_{resultado['data_decisao']:%Y%m%d}"
    componentes = {k: v for k, v in resultado.items() if not isinstance(v, (list, np.ndarray))}
    pd.DataFrame([componentes]).to_csv(pasta / f"pedido_{sufixo}.csv", index=False)
    previsao_diaria.round(2).to_csv(pasta / f"previsao_diaria_{sufixo}.csv")
    print(f"\nArquivos salvos em saidas/: pedido_{sufixo}.csv e previsao_diaria_{sufixo}.csv")


if __name__ == "__main__":
    main()
