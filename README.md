# Trabalho Final — Recuperação da Informação (2026.1)

**Disciplina:** Recuperação da Informação
**Curso:** Bacharelado em Ciência de Dados e Machine Learning — CEUB
**Professor:** MSc. Weslley Rodrigues
**Entrega e apresentação:** 22/06/2026

> Este é o repositório-modelo da disciplina. Façam um **fork** deste repositório, renomeiem para o grupo de vocês (ex.: `trabalho-final-rdi-grupo-3`) e sigam as orientações abaixo.

---

## Sobre o trabalho

O objetivo é integrar e analisar **duas bases de dados reais** usando técnicas de Recuperação da Informação, e comunicar os achados com clareza.

- **Base 1 — State of Data Brazil (2021–2025):** vocês vão **consolidar** as edições da pesquisa em um único arquivo `.parquet`, exatamente como fizemos em aula. O script de consolidação faz parte do trabalho.
- **Base 2 — Fonte externa (escolha do grupo):** dados abertos coletados **obrigatoriamente** via Web Scraping ou API pública. A coleta tem que estar no repositório e ser reproduzível.

O projeto precisa rodar **do início ao fim** sem etapas manuais escondidas: da coleta à geração do relatório.

---

## Como começar (passo a passo)

1. **Fork** deste repositório (botão *Fork*, no canto superior direito).
2. Em *Settings → General*, deixem o repositório **privado**.
3. Em *Settings → Collaborators*, adicionem o professor: **`Professor-Weslley`**.
4. Renomeiem o repositório para o nome do grupo.
5. Cada integrante clona, trabalha e faz **commits com o e-mail institucional** (`@sempreceub.com`). Todos precisam aparecer no histórico.
6. Preencham este README com as informações do grupo (seção abaixo) e desenvolvam o projeto.

---

## Estrutura sugerida

Esta é uma estrutura **mínima** — sintam-se livres para adicionar pastas conforme a necessidade do projeto de vocês. O que importa é que esteja organizado e reproduzível.

> **Sobre os dados:** o `.gitignore` deste template **não versiona** os arquivos pesados (CSVs brutos e o `.parquet` gerado) — eles são reconstruídos rodando os scripts de `src/coleta/`. É isso que torna o projeto reprodutível: quem clonar roda os scripts e regenera os dados. Se a base externa de vocês for pequena e quiserem versioná-la, é só ajustar o `.gitignore`.

```
.
├── README.md              ← este arquivo (preencham a seção do grupo)
├── data/                  ← dados (brutos e tratados); o .parquet gerado vai aqui
├── src/
│   ├── coleta/            ← scripts de coleta das DUAS bases
│   │   ├── consolida_state_of_data.(py|R)   ← gera o .parquet do State of Data
│   │   └── coleta_externa.(py|R)            ← scraping ou API da base externa
│   └── limpeza/           ← limpeza, padronização e integração das bases
├── relatorio.(qmd|ipynb)  ← relatório-fonte (vira o PDF da entrega)
└── docs/                  ← PDF final e materiais de apoio
```

---

## O que entregar

Dois itens, **no Moodle**:

1. **Relatório em PDF** (anexado na tarefa) — gerado a partir do `relatorio.qmd` / `.ipynb`.
2. **Link deste repositório** (colado no texto da entrega).

### Checklist antes de enviar

- [ ] Scripts de coleta das duas bases em `src/coleta/`
- [ ] Script de consolidação do State of Data, gerando o `.parquet`
- [ ] Script de coleta da base externa (scraping ou API)
- [ ] Limpeza e integração em `src/limpeza/`
- [ ] Pelo menos **um modelo de RI** aplicado (Booleano, Vetorial/TF-IDF, BM25, Dense/embeddings)
- [ ] Visualizações analíticas com interpretação
- [ ] Relatório-fonte (`.qmd` ou `.ipynb`) + PDF gerado a partir dele
- [ ] Este README preenchido
- [ ] Repositório **privado** com `Professor-Weslley` como colaborador
- [ ] Commits de **todos** os integrantes
- [ ] Projeto reproduzível do início ao fim

---

## Avaliação

Avaliado com base no **código, na análise, na organização do repositório e na entrega técnica completa**.

---

## Como executar (preencham)

> Expliquem aqui, em poucos passos, como rodar o projeto de vocês do zero. Exemplo:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Consolidar o State of Data (gera o .parquet em data/)
python src/coleta/consolida_state_of_data.py

# 3. Coletar a base externa
python src/coleta/coleta_externa.py

# 4. Limpar e integrar
python src/limpeza/integra.py

# 5. Gerar o relatório
quarto render relatorio.qmd
```

---

## Identificação do grupo (preencham)

**Nome do grupo:**

**Tema / pergunta de pesquisa:**

**Base externa escolhida (fonte + método de coleta):**

**Integrantes:**

| Nome | Matrícula | E-mail institucional | Usuário GitHub |
|------|-----------|----------------------|----------------|
|      |           |                      |                |
|      |           |                      |                |
|      |           |                      |                |

**Modelo(s) de RI utilizado(s):**

**Resumo do projeto (3–5 linhas):**
