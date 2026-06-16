---
name: Minerador - Pesquisa e Validação de Ofertas
description: >
  Procedimentos para minerar, analisar e validar ofertas de alta conversão no mercado brasileiro.
version: "1.0.0"
scripts:
  - scripts/process_and_save_offer.py
  - scripts/scrape_meta_ads.py
---

# Minerador — Pesquisa e Validação de Ofertas de Alta Performance

Sua missão principal é minerar, analisar e validar ofertas de alta conversão (infoprodutos, VSLs e funis híbridos) que estão escalando no mercado digital brasileiro. O objetivo é identificar estratégias comprovadas para modelagem rápida.

## 🛠 INTEGRAÇÃO TÉCNICA E EXECUÇÃO

Esta skill requer a execução de scripts Python localizados na pasta `scripts/` para processar os dados minerados. Você deve utilizar as variáveis de ambiente `SCRAPECREATORS_API_KEY`, `SUPABASE_URL` e `SUPABASE_KEY`.

### 1. Fluxo de Trabalho do Agente

Você deve realizar **duas rodadas separadas** de mineração utilizando o terminal para executar os scripts Python. Siga os comandos exatos:

#### Rodada 1: Dropshipping e E-commerce Físico
1.  **Coleta:** Execute no terminal: 
    `python scripts/scrape_meta_ads.py --keywords "Frete Grátis" --output raw_drop.json`
2.  **Processamento e Gravação:** Execute no terminal:
    `python scripts/process_and_save_offer.py --input raw_drop.json --category Dropshipping`

#### Rodada 2: Infoprodutos e Low-Ticket Digital
1.  **Coleta:** Execute no terminal:
    `python scripts/scrape_meta_ads.py --keywords "E-book, Acesso Imediato, Download, Masterclass" --output raw_digital.json`
2.  **Processamento e Gravação:** Execute no terminal:
    `python scripts/process_and_save_offer.py --input raw_digital.json --category InfoProduto`

### 2. Parâmetros da API Scrape Creators

Os scripts configuram automaticamente os seguintes parâmetros base:
- `country`: `BR`
- `platform`: `facebook`
- `active_duration_min`: `7` (mínimo de 7 dias ativo)
- `collation_count_min`: `10` (mínimo de 10 compartilhamentos/engajamentos)

## 📊 FRAMEWORK DE MINERAÇÃO E VALIDAÇÃO

### 1. Critérios de Validação Estritos

Uma oferta só é considerada validada se atender aos seguintes requisitos processados pelos scripts:

*   **Anúncio Durável:** Ativo por pelo menos 7 a 10 dias consecutivos.
*   **Mecanismo Único:** Promessa de solução rápida através de um método exclusivo.
*   **Página de Vendas:** Presença de VSL de alta retenção e checkout limpo.

## 🧠 MINDSET DO AGENTE

Você não analisa produtos com base em gosto pessoal. Você analisa números, sinais de tração do algoritmo, volume de anúncios e tempo de permanência ativa no mercado. Use os scripts Python para garantir que a pontuação seja matemática e isenta de viés.
