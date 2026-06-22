"""
consolida_state_of_data.py
--------------------------
Lê os CSVs anuais do State of Data Brazil (2021-2024),
padroniza as colunas de interesse e gera um único arquivo
.parquet em data/processed/.

Contexto:
  - 2021-2023: colunas no formato string de tupla, ex: "('P2_h ', 'Faixa salarial')"
  - 2024: colunas no formato 'secao.questao_label', ex: '2.h_faixa_salarial'
  O script trata os dois formatos e produz um dataset limpo com nomes padronizados.

Entrada : data/raw/state_of_data_2021.csv  ... state_of_data_2024.csv
Saída   : data/processed/dados_state_of_data_consolidados.parquet

Uso:
    python src/coleta/consolida_state_of_data.py
"""

import ast
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ARQUIVOS = {
    2021: RAW_DIR / "state_of_data_2021.csv",
    2022: RAW_DIR / "state_of_data_2022.csv",
    2023: RAW_DIR / "state_of_data_2023.csv",
    2024: RAW_DIR / "state_of_data_2024.csv",
}

# ---------------------------------------------------------------------------
# Mapeamento de colunas
#
# Para 2021-2023: chave = código da questão (ex: 'P2_h')
# Para 2024: chave = nome exato da coluna no CSV
# Valor: nome padronizado final
# ---------------------------------------------------------------------------

# 2021-2023: código da questão → nome final
# Nota: alguns códigos mudaram entre anos (ex: estado = P1_e em 2021, P1_i em 2022-2023)
CODIGOS_2021_2023 = {
    "P1_a_a": "faixa_idade",            # 2021
    "P1_a_1": "faixa_idade",            # 2022-2023
    "P1_b":   "genero",
    "P1_c":   "cor_raca_etnia",         # não existe em 2021
    "P1_e":   "estado",                 # 2021
    "P1_i":   "estado",                 # 2022-2023
    "P1_h":   "nivel_ensino",           # 2021
    "P1_l":   "nivel_ensino",           # 2022-2023
    "P2_f":   "cargo_atual",
    "P2_h":   "faixa_salarial",
    "P2_i":   "tempo_experiencia_dados",
    "P4_e":   "linguagem_mais_usada",
}

# 2024: coluna exata no CSV → nome final
COLUNAS_2024 = {
    "1.a.1_faixa_idade":                 "faixa_idade",
    "1.b_genero":                        "genero",
    "1.c_cor/raca/etnia":                "cor_raca_etnia",
    "1.i_estado_onde_mora":              "estado",
    "1.l_nivel_de_ensino":               "nivel_ensino",
    "2.f_cargo_atual":                   "cargo_atual",
    "2.h_faixa_salarial":                "faixa_salarial",
    "2.i_tempo_de_experiencia_em_dados": "tempo_experiencia_dados",
    "4.e_linguagem_mais_usada":          "linguagem_mais_usada",
}

COLUNAS_FINAIS = [
    "ano",
    "faixa_idade",
    "genero",
    "cor_raca_etnia",
    "estado",
    "nivel_ensino",
    "cargo_atual",
    "faixa_salarial",
    "tempo_experiencia_dados",
    "linguagem_mais_usada",
]

# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------


def extrair_codigo_e_label(col: str) -> tuple[str, str]:
    """
    Extrai o código e o label de uma coluna no formato tupla-string.
    "('P2_h ', 'Faixa salarial')"  →  ('P2_h', 'Faixa salarial')
    """
    try:
        tup = ast.literal_eval(col)
        codigo = tup[0].strip() if len(tup) > 0 else col.strip()
        label  = tup[1].strip() if len(tup) > 1 else ""
        return codigo, label
    except Exception:
        return col.strip(), ""


# Labels que confirmam que a coluna é realmente "estado onde mora"
_LABELS_ESTADO = {"estado onde mora", "uf onde mora"}


def carregar_2021_2023(ano: int, caminho: Path) -> pd.DataFrame:
    """Lê um CSV de 2021-2023 e retorna DataFrame com colunas padronizadas."""
    df = pd.read_csv(caminho, low_memory=False)

    renomear = {}
    nomes_ja_usados = set()

    for col in df.columns:
        codigo, label = extrair_codigo_e_label(col)
        if codigo not in CODIGOS_2021_2023:
            continue

        nome_final = CODIGOS_2021_2023[codigo]

        # Validação extra para "estado": confirma pelo label para evitar
        # mapear P1_e de 2022 (experiência profissional) como estado
        if nome_final == "estado" and label.lower() not in _LABELS_ESTADO:
            continue

        # Evita mapear dois códigos diferentes para o mesmo nome final
        if nome_final not in nomes_ja_usados:
            renomear[col] = nome_final
            nomes_ja_usados.add(nome_final)

    df = df.rename(columns=renomear)

    # Seleciona apenas as colunas mapeadas que existem no df
    colunas_presentes = [c for c in COLUNAS_FINAIS[1:] if c in df.columns]
    df = df[colunas_presentes].copy()
    df.insert(0, "ano", ano)
    return df


def carregar_2024(caminho: Path) -> pd.DataFrame:
    """Lê o CSV de 2024 e retorna DataFrame com colunas padronizadas."""
    df = pd.read_csv(caminho, low_memory=False)

    colunas_presentes = {k: v for k, v in COLUNAS_2024.items() if k in df.columns}
    df = df[list(colunas_presentes.keys())].rename(columns=colunas_presentes)

    colunas_finais_presentes = [c for c in COLUNAS_FINAIS[1:] if c in df.columns]
    df = df[colunas_finais_presentes].copy()
    df.insert(0, "ano", 2024)
    return df


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------


def consolidar() -> pd.DataFrame:
    partes = []

    for ano, caminho in ARQUIVOS.items():
        if not caminho.exists():
            print(f"[AVISO] Arquivo não encontrado, pulando: {caminho.name}")
            continue

        print(f"  Lendo {ano}...", end=" ")

        df = carregar_2024(caminho) if ano == 2024 else carregar_2021_2023(ano, caminho)

        print(f"{len(df):,} linhas | colunas: {list(df.columns)}")
        partes.append(df)

    if not partes:
        raise FileNotFoundError(
            "Nenhum CSV encontrado em data/raw/.\n"
            "Nomeie os arquivos como:\n"
            "  state_of_data_2021.csv\n"
            "  state_of_data_2022.csv\n"
            "  state_of_data_2023.csv\n"
            "  state_of_data_2024.csv"
        )

    df_final = pd.concat(partes, ignore_index=True)
    df_final["ano"] = df_final["ano"].astype(int)

    # Remove linhas completamente vazias (exceto 'ano')
    cols_dados = [c for c in df_final.columns if c != "ano"]
    df_final = df_final.dropna(how="all", subset=cols_dados).reset_index(drop=True)

    return df_final


def main():
    print("=" * 55)
    print("  Consolidação — State of Data Brazil 2021-2024")
    print("=" * 55)

    df = consolidar()

    print(f"\nDataset consolidado: {df.shape[0]:,} linhas x {df.shape[1]} colunas")

    print("\nRespondentes por ano:")
    print(df["ano"].value_counts().sort_index().to_string())

    print("\nCobertura das colunas:")
    for col in df.columns:
        n = df[col].notna().sum()
        pct = n / len(df) * 100
        print(f"  {col:<30} {n:>6,} ({pct:.1f}%)")

    destino = PROCESSED_DIR / "dados_state_of_data_consolidados.parquet"
    df.to_parquet(destino, index=False, engine="pyarrow")

    print(f"\nParquet salvo em: {destino.relative_to(ROOT)}")
    print("Consolidação concluída.")


if __name__ == "__main__":
    main()
