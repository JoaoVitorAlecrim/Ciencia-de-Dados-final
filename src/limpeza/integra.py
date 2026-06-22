"""
integra.py
----------
Limpeza, padronização e integração das duas bases:
  - State of Data Brazil 2021-2024 (consolidado em .parquet)
  - Google Trends 2021-2024 (série temporal + por estado)

Saídas:
  data/processed/sod_limpo.parquet         — State of Data limpo
  data/processed/trends_limpo.parquet      — Trends por estado limpo
  data/processed/base_integrada.parquet    — dataset integrado (join por estado+ano)

Uso:
    python src/limpeza/integra.py
"""

import re
from pathlib import Path

import pandas as pd

PROC = Path("data/processed")
RAW  = Path("data/raw")
PROC.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Mapa de normalização de estados
# State of Data usa nomes como "São Paulo", "Rio de Janeiro"
# Google Trends pode retornar "State of São Paulo" ou variações
# ---------------------------------------------------------------------------

ESTADO_PARA_UF = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
    "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF",
    "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA",
    "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
    "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE",
    "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
    "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE",
    "Tocantins": "TO",
}

# Alguns nomes alternativos que o Google Trends pode retornar
ALIAS_ESTADOS = {
    "State of São Paulo": "SP",
    "State of Rio de Janeiro": "RJ",
    "State of Minas Gerais": "MG",
    "State of Bahia": "BA",
    "State of Paraná": "PR",
    "State of Rio Grande do Sul": "RS",
    "State of Santa Catarina": "SC",
    "State of Goiás": "GO",
    "State of Pernambuco": "PE",
    "State of Ceará": "CE",
    "Federal District": "DF",
}


def normalizar_uf(nome: str) -> str | None:
    """Converte nome de estado (qualquer formato) para sigla de 2 letras."""
    if pd.isna(nome):
        return None
    nome = str(nome).strip()

    # Formato do State of Data: "São Paulo (SP)" → extrai "SP"
    match = re.search(r"\(([A-Z]{2})\)$", nome)
    if match:
        return match.group(1)

    # Nome completo direto
    if nome in ESTADO_PARA_UF:
        return ESTADO_PARA_UF[nome]

    # Alias do Google Trends ("State of São Paulo", "Federal District", etc.)
    if nome in ALIAS_ESTADOS:
        return ALIAS_ESTADOS[nome]

    # Remove "State of " e tenta novamente
    sem_prefix = re.sub(r"^State of\s+", "", nome, flags=re.IGNORECASE).strip()
    if sem_prefix in ESTADO_PARA_UF:
        return ESTADO_PARA_UF[sem_prefix]

    return None


# ---------------------------------------------------------------------------
# Extração do ponto médio da faixa salarial
# Ex: "de R$ 4.001/mês a R$ 6.000/mês" → 5000.5
# ---------------------------------------------------------------------------

def extrair_salario_medio(faixa: str) -> float | None:
    if pd.isna(faixa):
        return None
    numeros = re.findall(r"[\d\.]+", str(faixa))
    numeros = [float(n.replace(".", "")) for n in numeros if n.replace(".", "").isdigit()]
    if len(numeros) >= 2:
        return (numeros[0] + numeros[1]) / 2
    if len(numeros) == 1:
        return numeros[0]
    return None


# ---------------------------------------------------------------------------
# Agrupamento de cargos
# ---------------------------------------------------------------------------

def agrupar_cargo(cargo: str) -> str:
    if pd.isna(cargo):
        return "Outro"
    cargo_lower = str(cargo).lower()
    if any(t in cargo_lower for t in ["analista de dados", "data analyst"]):
        return "Analista de Dados"
    if any(t in cargo_lower for t in ["cientista de dados", "data scientist"]):
        return "Cientista de Dados"
    if any(t in cargo_lower for t in ["engenheiro de dados", "data engineer"]):
        return "Engenheiro de Dados"
    if any(t in cargo_lower for t in ["analytics engineer"]):
        return "Analytics Engineer"
    if any(t in cargo_lower for t in ["machine learning", "ml engineer", "ai "]):
        return "ML/IA Engineer"
    if any(t in cargo_lower for t in ["gestor", "manager", "head", "diretor", "líder"]):
        return "Gestor/Liderança"
    if any(t in cargo_lower for t in ["bi", "business intelligence"]):
        return "BI/Dados"
    return "Outro"


# ---------------------------------------------------------------------------
# Limpeza — State of Data
# ---------------------------------------------------------------------------

def limpar_sod(caminho: Path) -> pd.DataFrame:
    print("Carregando State of Data...")
    df = pd.read_parquet(caminho, engine="pyarrow")
    print(f"  Shape original: {df.shape}")

    # Normaliza estado → sigla UF
    df["uf"] = df["estado"].apply(normalizar_uf)

    # Salário numérico
    df["salario_medio"] = df["faixa_salarial"].apply(extrair_salario_medio)

    # Cargo agrupado
    df["cargo_grupo"] = df["cargo_atual"].apply(agrupar_cargo)

    # Remove linhas sem UF ou sem ano
    df = df.dropna(subset=["uf", "ano"])
    df["ano"] = df["ano"].astype(int)

    # Padroniza linguagem (strip + title case)
    df["linguagem_mais_usada"] = df["linguagem_mais_usada"].str.strip()

    print(f"  Shape limpo:    {df.shape}")
    print(f"  Anos: {sorted(df['ano'].unique())}")
    print(f"  UFs únicas: {df['uf'].nunique()}")
    return df


# ---------------------------------------------------------------------------
# Limpeza — Google Trends por estado
# ---------------------------------------------------------------------------

def limpar_trends(caminho: Path) -> pd.DataFrame:
    print("\nCarregando Google Trends por estado...")
    df = pd.read_csv(caminho)
    print(f"  Shape original: {df.shape}")

    # Normaliza estado → sigla UF
    df["uf"] = df["estado"].apply(normalizar_uf)

    # Remove estados não reconhecidos
    df = df.dropna(subset=["uf"])
    df["ano"] = df["ano"].astype(int)

    # Remove interesse zero (estado sem dados suficientes)
    df = df[df["interesse"] > 0]

    print(f"  Shape limpo:    {df.shape}")
    print(f"  Anos: {sorted(df['ano'].unique())}")
    print(f"  Termos únicos: {df['termo'].nunique()}")
    return df


# ---------------------------------------------------------------------------
# Integração — agrega State of Data por UF+ano e une com Trends
# ---------------------------------------------------------------------------

def integrar(df_sod: pd.DataFrame, df_trends: pd.DataFrame) -> pd.DataFrame:
    print("\nIntegrando bases...")

    # Agrega State of Data por UF e ano
    agg_sod = (
        df_sod.groupby(["uf", "ano"])
        .agg(
            n_respondentes=("uf", "count"),
            salario_mediano=("salario_medio", "median"),
            linguagem_top=("linguagem_mais_usada", lambda x: x.value_counts().idxmax() if x.notna().any() else None),
            cargo_top=("cargo_grupo", lambda x: x.value_counts().idxmax()),
            pct_python=("linguagem_mais_usada", lambda x: (x == "Python").sum() / x.notna().sum() * 100 if x.notna().any() else 0),
            pct_sql=("linguagem_mais_usada", lambda x: (x == "SQL").sum() / x.notna().sum() * 100 if x.notna().any() else 0),
        )
        .reset_index()
    )

    # Agrega Trends por UF e ano (interesse médio por grupo de termos)
    agg_trends = (
        df_trends.groupby(["uf", "ano", "grupo"])["interesse"]
        .mean()
        .round(1)
        .reset_index()
        .pivot_table(index=["uf", "ano"], columns="grupo", values="interesse")
        .reset_index()
    )
    agg_trends.columns.name = None
    # Renomeia colunas de grupo com prefixo "trends_"
    for col in ["linguagens", "ferramentas", "carreiras"]:
        if col in agg_trends.columns:
            agg_trends = agg_trends.rename(columns={col: f"trends_{col}"})

    # Join por UF + ano
    df_integrado = agg_sod.merge(agg_trends, on=["uf", "ano"], how="inner")

    print(f"  Shape integrado: {df_integrado.shape}")
    print(f"  Pares UF×ano: {len(df_integrado)}")
    return df_integrado


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Limpeza e Integração — State of Data × Google Trends")
    print("=" * 55 + "\n")

    # Limpeza individual
    df_sod = limpar_sod(PROC / "dados_state_of_data_consolidados.parquet")
    df_trends = limpar_trends(RAW / "trends_por_estado.csv")

    # Salva versões limpas
    df_sod.to_parquet(PROC / "sod_limpo.parquet", index=False, engine="pyarrow")
    df_trends.to_parquet(PROC / "trends_limpo.parquet", index=False, engine="pyarrow")
    print("\nArquivos limpos salvos.")

    # Integração
    df_integrado = integrar(df_sod, df_trends)
    df_integrado.to_parquet(PROC / "base_integrada.parquet", index=False, engine="pyarrow")

    print(f"\nBase integrada salva em data/processed/base_integrada.parquet")
    print("\nAmostra:")
    print(df_integrado.head(5).to_string(index=False))
    print("\nIntegração concluída.")


if __name__ == "__main__":
    main()
