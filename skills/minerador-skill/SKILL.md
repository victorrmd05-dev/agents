---
name: Minerador - Offer Research and Validation
description: Procedures for mining, analyzing, and validating high-conversion offers in the Brazilian market.
version: "1.0.0"
---

# Minerador — High-Performance Offer Research and Validation

Your primary mission is to mine, analyze, and validate high-conversion offers (infoproducts, VSLs, and hybrid funnels) that are currently scaling in the Brazilian digital market. The objective is to identify proven strategies for rapid modeling.

## 🛠 TECHNICAL INTEGRATION AND EXECUTION

This skill requires the execution of Python scripts located in the `scripts/` folder to process the mined data. You must use the environment variables `SCRAPECREATORS_API_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY`.

### 1. Agent Workflow

You must perform **two separate rounds** of mining using the terminal to execute the Python scripts. Follow the exact commands:

#### Round 1: Dropshipping and Physical E-commerce
1.  **Collection:** Execute in the terminal: 
    `python scripts/scrape_meta_ads.py --keywords "Frete Grátis" --output raw_drop.json`
2.  **Processing and Saving:** Execute in the terminal:
    `python scripts/process_and_save_offer.py --input raw_drop.json --category Dropshipping`

#### Round 2: Infoproducts and Low-Ticket Digital
1.  **Collection:** Execute in the terminal:
    `python scripts/scrape_meta_ads.py --keywords "E-book, Acesso Imediato, Download, Masterclass" --output raw_digital.json`
2.  **Processing and Saving:** Execute in the terminal:
    `python scripts/process_and_save_offer.py --input raw_digital.json --category InfoProduto`

### 2. Scrape Creators API Parameters

The scripts automatically configure the following base parameters:
- `country`: `BR`
- `platform`: `facebook`
- `active_duration_min`: `7` (minimum 7 days active)
- `collation_count_min`: `10` (minimum 10 shares/engagements)

## 📊 MINING AND VALIDATION FRAMEWORK

### 1. Strict Validation Criteria

An offer is only considered validated if it meets the following requirements, processed by the scripts:

*   **Durable Ad:** Active for at least 7 to 10 consecutive days.
*   **Unique Mechanism:** Promise of a quick solution through an exclusive method.
*   **Sales Page:** Presence of a high-retention VSL and a clean checkout.

## 🧠 AGENT MINDSET

You do not analyze products based on personal taste. You analyze numbers, signs of algorithm traction, ad volume, and active market presence duration. Use the Python scripts to ensure the scoring is mathematical and free from bias.
