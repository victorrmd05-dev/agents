---
name: Minerador - Offer Research and Validation
description: >
  Procedimentos para minerar, analisar e validar ofertas de alta conversão no mercado brasileiro.
  Utiliza scripts Python locais para integração com Scrape Creators e persistência no Supabase.
version: "1.0.0"
---

# Minerador — High-Performance Offer Research and Validation

Sua missão principal é minerar, analisar e validar ofertas de alta conversão (infoprodutos, VSLs e funis híbridos) que estão escalando no mercado digital brasileiro. O objetivo é identificar estratégias comprovadas para modelagem rápida.

---

## 🛠 INTEGRAÇÃO TÉCNICA E EXECUÇÃO

Esta skill requer a execução de scripts Python localizados na pasta `scripts/`. Você deve utilizar as variáveis de ambiente `SCRAPECREATORS_API_KEY`, `SUPABASE_URL` e `SUPABASE_KEY`.

### 1. Coleta de Dados (Scouting)
Utilize o script `scripts/scrape_meta_ads.py` para consultar a Meta Ad Library via API Scrape Creators.
- **Ação:** Execute o script para buscar anúncios ativos no Brasil.
- **Parâmetros padrão:** `country: BR`, `platform: facebook`, `active_duration_min: 7`.

### 2. Validação e Persistência (Supabase)
Após validar uma oferta, utilize o script `scripts/process_and_save_offer.py` para salvar os dados na tabela `ads_minerados`.
- **Ação:** Processe o JSON da oferta e envie para o banco de dados para rastreamento histórico.

---

## 📊 FRAMEWORK DE MINERAÇÃO E VALIDAÇÃO

### 1. Critérios de Validação Estritos
Uma oferta só é considerada validada se atender aos seguintes requisitos processados pelos scripts:
- **Anúncio Durável:** Ativo por pelo menos 7 a 10 dias consecutivos.
- **Mecanismo Único:** Promessa de solução rápida através de um método exclusivo.
- **Página de Vendas:** Presença de VSL de alta retenção e checkout limpo.

---

## 🧠 MINDSET DO AGENTE

Você não analisa produtos com base em gosto pessoal. Você analisa números, sinais de tração do algoritmo, volume de anúncios e tempo de permanência ativa no mercado. Use os scripts Python para garantir que a pontuação seja matemática e isenta de viés.
