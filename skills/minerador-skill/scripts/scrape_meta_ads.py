#!/usr/bin/env python3
"""
Minerador — Scraper da Biblioteca de Anúncios Meta
Uso: python scripts/scrape_meta_ads.py --keywords "Frete Grátis" --output raw_drop.json
"""
import os
import requests
import json
import argparse
import sys

# ─── Filtros de qualidade (anúncios que valem atenção) ───────────────────────
ACTIVE_DURATION_MIN = 7      # mínimo de dias ativo
COLLATION_COUNT_MIN = 10     # mínimo de engajamentos/compartilhamentos
MAX_RESULTS = 50             # limite por chamada

def scrape_meta_ads(api_key: str, keywords: str, country: str = "BR", platform: str = "facebook") -> list:
    url = "https://api.scrapecreators.com/v1/meta-ads/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "country": country,
        "platform": platform,
        "active_duration_min": ACTIVE_DURATION_MIN,
        "collation_count_min": COLLATION_COUNT_MIN,
        "limit": MAX_RESULTS,
        "keywords": keywords
    }

    print(f"[scraper] Buscando anúncios | keywords: '{keywords}' | país: {country}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"[ERRO HTTP] {e} — Resposta: {response.text[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)

    # A API pode retornar lista direta ou dentro de uma chave
    if isinstance(data, list):
        ads = data
    elif isinstance(data, dict):
        ads = data.get("ads") or data.get("results") or data.get("data") or []
    else:
        ads = []

    print(f"[scraper] {len(ads)} anúncios recebidos da API")

    # ─── Filtragem cirúrgica local (dupla garantia) ──────────────────────────
    filtered = []
    for ad in ads:
        duration = ad.get("active_duration") or ad.get("days_active") or 0
        collation = ad.get("collation_count") or ad.get("engagement") or 0

        # Garante os filtros mesmo que a API ignore os params
        if duration < ACTIVE_DURATION_MIN:
            continue
        if collation < COLLATION_COUNT_MIN:
            continue

        # Remove anúncios sem página de destino (lixo sem funil)
        if not ad.get("ad_snapshot_url") and not ad.get("page_id"):
            continue

        filtered.append(ad)

    print(f"[scraper] {len(filtered)} anúncios após filtragem de qualidade")
    return filtered


def main():
    parser = argparse.ArgumentParser(description="Scraper da Biblioteca de Anúncios Meta")
    parser.add_argument("--keywords", required=True, help='Palavras-chave (ex: "Frete Grátis")')
    parser.add_argument("--output", required=True, help="Arquivo JSON de saída (ex: raw_drop.json)")
    parser.add_argument("--country", default="BR", help="País (padrão: BR)")
    parser.add_argument("--platform", default="facebook", help="Plataforma (padrão: facebook)")
    args = parser.parse_args()

    api_key = os.getenv("SCRAPECREATORS_API_KEY")
    if not api_key:
        print("[ERRO] Variável de ambiente SCRAPECREATORS_API_KEY não encontrada.")
        sys.exit(1)

    ads = scrape_meta_ads(
        api_key=api_key,
        keywords=args.keywords,
        country=args.country,
        platform=args.platform
    )

    if not ads:
        print("[AVISO] Nenhum anúncio passou pelos filtros. Verifique os parâmetros.")
        # Salva arquivo vazio para não quebrar o próximo script
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump([], f)
        sys.exit(0)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)

    print(f"[scraper] ✓ Salvo em '{args.output}' com {len(ads)} anúncios prontos para análise.")


if __name__ == "__main__":
    main()
