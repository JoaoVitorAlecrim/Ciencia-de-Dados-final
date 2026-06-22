# Guia de Commits — Um por Integrante

Cada integrante deve seguir os passos abaixo para commitar a sua parte no repositório.

---

## Pré-requisito (todos)

1. Instale o Git: https://git-scm.com/downloads
2. Configure seu nome e email (use o mesmo email do GitHub):
   ```bash
   git config --global user.name "Seu Nome"
   git config --global user.email "seu@email.com"
   ```
3. Clone o repositório (peça o link ao João Vitor):
   ```bash
   git clone https://github.com/usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

---

## Integrante 1 — Coleta State of Data

Arquivos sob sua responsabilidade:
- `src/coleta/consolida_state_of_data.py`
- `data/raw/state_of_data_2021.csv`
- `data/raw/state_of_data_2022.csv`
- `data/raw/state_of_data_2023.csv`
- `data/raw/state_of_data_2024.csv`

Comandos:
```bash
git add src/coleta/consolida_state_of_data.py
git add data/raw/state_of_data_2021.csv data/raw/state_of_data_2022.csv
git add data/raw/state_of_data_2023.csv data/raw/state_of_data_2024.csv
git commit -m "feat: script de consolidação do State of Data 2021-2024"
git push origin main
```

---

## Integrante 2 — Coleta Externa (Google Trends)

Arquivos sob sua responsabilidade:
- `src/coleta/coleta_externa.py`
- `data/raw/trends_serie_temporal.csv`
- `data/raw/trends_por_estado.csv`

Comandos:
```bash
git add src/coleta/coleta_externa.py
git add data/raw/trends_serie_temporal.csv data/raw/trends_por_estado.csv
git commit -m "feat: coleta de dados do Google Trends via pytrends (2021-2024)"
git push origin main
```

---

## Integrante 3 — Limpeza e Integração

Arquivos sob sua responsabilidade:
- `src/limpeza/integra.py`
- `data/processed/dados_state_of_data_consolidados.parquet`
- `data/processed/sod_limpo.parquet`
- `data/processed/trends_limpo.parquet`
- `data/processed/base_integrada.parquet`

Comandos:
```bash
git add src/limpeza/integra.py
git add data/processed/
git commit -m "feat: limpeza, padronização e integração das bases de dados"
git push origin main
```

---

## Integrante 4 — Relatório e Análise (João Vitor)

Arquivos sob sua responsabilidade:
- `relatorio.qmd`
- `relatorio.html`
- `relatorio.pdf`
- `docs/` (gráficos gerados)
- `requirements.txt`
- `README.md`

Comandos:
```bash
git add relatorio.qmd relatorio.html relatorio.pdf
git add docs/
git add requirements.txt README.md
git commit -m "feat: relatório completo com TF-IDF, visualizações e análise"
git push origin main
```

---

## Observações

- Façam os commits **em ordem** (1 → 2 → 3 → 4) para evitar conflitos.
- Se aparecer erro de conflito ao fazer `push`, rode `git pull origin main` antes e tente novamente.
- O repositório deve estar como **privado** nas configurações do GitHub, com o professor adicionado como colaborador.
