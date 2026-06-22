"""
coleta_externa.py
-----------------
Coleta dados do Google Trends via pytrends (API pública, sem autenticação).

Dados coletados para termos relacionados a dados/tecnologia no Brasil:
  1. Série temporal mensal (2021-2024) — interesse ao longo do tempo por termo
  2. Interesse por estado brasileiro (UF) — por ano e por termo

Os termos foram escolhidos para espelhar as linguagens e ferramentas
presentes no questionário do State of Data Brazil.

Saídas:
  data/raw/trends_serie_temporal.csv  — interesse mensal por termo
  data/raw/trends_por_estado.csv      — interesse por UF e ano

Uso:
    python src/coleta/coleta_externa.py
"""

import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

PASTA_RAW = Path("data/raw")

# pytrends: hl = idioma da interface, tz = fuso (180 = UTC-3, Brasília)
PYTRENDS = TrendReq(hl="pt-BR", tz=180)

# Termos alinhados com o questionário do State of Data Brazil.
# Máximo de 5 termos por grupo (limite da API do Google Trends).
GRUPOS_KEYWORDS = {
    "linguagens": ["Python", "SQL", "R", "Scala", "Julia"],
    "ferramentas": ["Power BI", "Tableau", "Apache Spark", "dbt", "Databricks"],
    "carreiras":   ["cientista de dados", "engenheiro de dados",
                    "analista de dados", "machine learning", "inteligencia artificial"],
}

ANOS = [2021, 2022, 2023, 2024]
GEO_BRASIL = "BR"

# Pausa entre requisições para evitar bloqueio por rate-limit
PAUSA_SEGUNDOS = 2

# ---------------------------------------------------------------------------
# Coleta 1 — Série temporal mensal (período completo 2021-2024)
# ---------------------------------------------------------------------------


def coletar_serie_temporal() -> pd.DataFrame:
    """Retorna interesse mensal por termo para o período completo."""
    print("\n--- Série temporal (2021–2024) ---")
    partes = []

    for grupo, keywords in GRUPOS_KEYWORDS.items():
        print(f"  [{grupo}] {keywords}")
        try:
            PYTRENDS.build_payload(
                keywords,
                geo=GEO_BRASIL,
                timeframe="2021-01-01 2024-12-31",
            )
            df = PYTRENDS.interest_over_time()

            if df.empty:
                print("    Sem dados retornados.")
                continue

            df = df.drop(columns=["isPartial"], errors="ignore")

            # Transforma de wide para long: uma linha por (data, termo)
            df = df.reset_index().melt(
                id_vars="date",
                var_name="termo",
                value_name="interesse",
            )
            df["grupo"] = grupo
            df["ano"] = df["date"].dt.year
            partes.append(df)

            print(f"    OK — {len(df):,} registros")

        except Exception as e:
            print(f"    ERRO: {e}")

        time.sleep(PAUSA_SEGUNDOS)

    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


# ---------------------------------------------------------------------------
# Coleta 2 — Interesse por estado, ano a ano
# ---------------------------------------------------------------------------


def coletar_por_estado() -> pd.DataFrame:
    """Retorna interesse médio por estado e por ano para cada termo."""
    print("\n--- Interesse por estado (ano a ano) ---")
    partes = []

    for ano in ANOS:
        timeframe = f"{ano}-01-01 {ano}-12-31"
        print(f"\n  Ano {ano}:")

        for grupo, keywords in GRUPOS_KEYWORDS.items():
            print(f"    [{grupo}] {keywords}")
            try:
                PYTRENDS.build_payload(
                    keywords,
                    geo=GEO_BRASIL,
                    timeframe=timeframe,
                )
                df = PYTRENDS.interest_by_region(
                    resolution="REGION",
                    inc_low_vol=True,
                    inc_geo_code=True,
                )

                if df.empty:
                    print("      Sem dados.")
                    continue

                # Transforma de wide para long
                df = df.reset_index().melt(
                    id_vars=["geoName", "geoCode"],
                    var_name="termo",
                    value_name="interesse",
                )
                df = df.rename(columns={"geoName": "estado", "geoCode": "estado_codigo"})
                df["ano"] = ano
                df["grupo"] = grupo
                partes.append(df)

                print(f"      OK — {len(df):,} registros")

            except Exception as e:
                print(f"      ERRO: {e}")

            time.sleep(PAUSA_SEGUNDOS)

    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------


def main():
    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    print("=" * 55)
    print("  Coleta Google Trends — Ferramentas de Dados BR")
    print("=" * 55)
    print(f"  Grupos: {list(GRUPOS_KEYWORDS.keys())}")
    print(f"  Anos: {ANOS}")
    print(f"  Termos por grupo: {list(GRUPOS_KEYWORDS.values())}")

    # --- Série temporal ---
    df_serie = coletar_serie_temporal()
    if not df_serie.empty:
        dest = PASTA_RAW / "trends_serie_temporal.csv"
        df_serie.to_csv(dest, index=False, encoding="utf-8-sig")
        print(f"\nSérie temporal salva: {dest} ({len(df_serie):,} registros)")
    else:
        print("\n[AVISO] Série temporal vazia.")

    # --- Por estado ---
    df_estados = coletar_por_estado()
    if not df_estados.empty:
        dest = PASTA_RAW / "trends_por_estado.csv"
        df_estados.to_csv(dest, index=False, encoding="utf-8-sig")
        print(f"\nPor estado salvo: {dest} ({len(df_estados):,} registros)")
    else:
        print("\n[AVISO] Dados por estado vazios.")

    print("\nColeta concluída.")


if __name__ == "__main__":
    main()
