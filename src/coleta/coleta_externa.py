"""
Coleta da BASE EXTERNA escolhida pelo grupo (Web Scraping OU API pública).

Este é um ESQUELETO. Adaptem para a fonte de vocês. O importante é que a
coleta fique reproduzível: quem clonar o repositório roda este script e
obtém os mesmos dados (salvos em data/raw/).

Lembrem das boas práticas que vimos em aula:
- definam um User-Agent na requisição;
- confiram o status da resposta antes de parsear;
- inspecionem o HTML recebido (nem sempre é igual ao do navegador);
- respeitem o robots.txt e os termos de uso do site.

SAÍDA: data/raw/base_externa.csv

Rode com:  python src/coleta/coleta_externa.py
"""

from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

PASTA_RAW = Path("data/raw")
ARQUIVO_SAIDA = PASTA_RAW / "base_externa.csv"

# Troquem pela URL / endpoint da fonte de vocês
URL = "https://exemplo.com/pagina-com-dados"
HEADERS = {"User-Agent": "Mozilla/5.0 (trabalho academico RDI CEUB)"}


def coletar() -> pd.DataFrame:
    """
    Exemplo MÍNIMO de scraping. Substituam os seletores pelos da página real.
    Se a fonte de vocês for uma API, troquem este corpo por requests.get(API).json().
    """
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    print(f"  status da requisição: {resp.status_code}")
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # >>> ADAPTEM: este seletor é só um exemplo <<<
    itens = soup.select("div.exemplo-item")
    registros = []
    for it in itens:
        registros.append({
            "titulo": it.select_one(".titulo").get_text(strip=True) if it.select_one(".titulo") else None,
            "valor":  it.select_one(".valor").get_text(strip=True) if it.select_one(".valor") else None,
        })

    df = pd.DataFrame(registros)
    print(f"  registros coletados: {len(df)}")
    return df


def main():
    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    print("Coletando base externa...")
    df = coletar()
    df.to_csv(ARQUIVO_SAIDA, index=False)
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
