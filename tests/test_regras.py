import numpy as np
import pandas as pd
import pytest

from src.backtest import gerar_origens, rodar_backtest
from src.metricas import vies, wmape
from src.pedido import sugerir_pedido
from src.pipeline import montar_futuro
from src.politica import estoque_seguranca_empirico, nivel_servico_otimo, simular_politica
from src.preparacao import H, remover_descontinuados, separar_treino_teste


@pytest.fixture
def serie():
    datas = pd.date_range("2019-01-01", periods=200, freq="D")
    return pd.DataFrame({"unidades": np.arange(200, dtype=float) + 100,
                         "pct_lojas_promo": 0.0, "preco_medio": 2.5}, index=datas)


def test_metricas_e_sinal_do_vies():
    real = np.array([100, 200, 100])
    assert wmape(real, real) == 0
    assert wmape(real, real * 1.1) == pytest.approx(10)
    assert vies(real, real * 1.1) == pytest.approx(10)
    assert vies(real, real * 0.9) == pytest.approx(-10)


def test_separacao_temporal_sem_sobreposicao(serie):
    treino, teste = separar_treino_teste(serie)
    assert len(teste) == H
    assert treino.index.max() < teste.index.min()
    assert len(treino) + len(teste) == len(serie)


def test_backtest_nunca_treina_com_o_futuro(serie):
    vistos = []

    def modelo_espiao(treino, futuro):
        vistos.append((treino.index.max(), futuro.index.min()))
        return np.zeros(len(futuro))

    origens = gerar_origens(serie)
    rodar_backtest(serie, {"espiao": modelo_espiao}, origens)
    assert origens[-1] == serie.index.max() - pd.Timedelta(days=H)
    assert all(fim_treino < inicio_futuro for fim_treino, inicio_futuro in vistos)
    assert all((o2 - o1).days == 14 for o1, o2 in zip(origens, origens[1:]))


def test_previsao_negativa_vira_zero(serie):
    resultado = rodar_backtest(serie, {"negativo": lambda t, f: -np.ones(len(f))}, gerar_origens(serie, n_origens=2))
    assert (resultado["previsto_total"] == 0).all()


def test_nivel_servico_e_estoque_seguranca():
    assert nivel_servico_otimo(0.30, 0.02) == pytest.approx(0.9375)
    assert estoque_seguranca_empirico(np.arange(1, 101), 0.5) == pytest.approx(50.5)


def test_simulacao_cobra_falta_e_sobra():
    bt = pd.DataFrame({"real_total": [100.0, 100.0], "previsto_total": [90.0, 110.0], "erro_unidades": [10.0, -10.0]})
    r = simular_politica(bt, 0.0, custo_falta=1.0, custo_sobra=0.1)
    assert r["estoque_seguranca_un"] == -10
    assert r["custo_medio_periodo_R$"] == pytest.approx((20 * 1.0 + 0) / 2 + 0 / 2)


def test_pedido_nao_fica_negativo(serie):
    futuro = pd.DataFrame({"pct_lojas_promo": 0.0}, index=pd.date_range("2019-07-20", periods=H))
    r = sugerir_pedido(serie, futuro, np.zeros(12), estoque_cd=1e9, nivel_servico=0.9375,
                       prever=lambda t, f: np.full(len(f), 10.0))
    assert r["pedido"] == 0
    assert r["demanda_prevista"] == pytest.approx(280)


def test_calendario_incompleto_e_rejeitado(serie):
    calendario = pd.DataFrame({"data": pd.date_range(serie.index.max() + pd.Timedelta(days=1), periods=10),
                               "pct_lojas_promo": 0.5})
    with pytest.raises(ValueError):
        montar_futuro(serie, calendario)


def test_descontinuados_saem_do_painel():
    painel = pd.DataFrame({"produto": ["P0131", "P0438", "P0051", "P0079"], "unidades": [1, 2, 3, 4]})
    assert remover_descontinuados(painel)["produto"].tolist() == ["P0131"]
