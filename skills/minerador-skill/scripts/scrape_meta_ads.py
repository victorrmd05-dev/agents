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

OURO_DURATION_MIN  = 25
OURO_COLLATION_MIN = 100

def scrape_meta_ads(api_key, keywords, country="BR", platform="facebook",
                    active_duration_min=7, collation_count_min=10, max_results=50):

    url = "https://api.scrapecreators.com/v1/meta-ads/search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    params  = {
        "country": country, "platform": platform,
        "active_duration_min": active_duration_min,
        "collation_count_min": collation_count_min,
        "limit": max_results, "keywords": keywords
    }

    print(f"[scraper] Buscando | keywords: '{keywords}' | ativo ≥ {active_duration_min}d | engaj ≥ {collation_count_min}")

    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.HTTPError as e:
        print(f"[ERRO HTTP] {e} — {r.text[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)

    if isinstance(data, list):
        ads = data
    elif isinstance(data, dict):
        ads = data.get("ads") or data.get("results") or data.get("data") or []
    else:
        ads = []

    print(f"[scraper] {len(ads)} anúncios recebidos da API")

    aprovados = []
    ouro      = []

    for ad in ads:
        duration  = ad.get("active_duration") or ad.get("days_active") or 0
        collation = ad.get("collation_count") or ad.get("engagement") or 0

        if duration  < active_duration_min:  continue
        if collation < collation_count_min:  continue
        if not ad.get("page_id") and not ad.get("page_name") and not ad.get("ad_snapshot_url"):
            continue

        if duration >= OURO_DURATION_MIN and collation >= OURO_COLLATION_MIN:
            ad["_ouro"] = True
            ouro.append(ad)
            print(f"  [OPORTUNIDADE OURO] {ad.get('page_name','?')} | {duration}d | {collation} engaj")

        aprovados.append(ad)

    print(f"[scraper] {len(aprovados)} aprovados | {len(ouro)} Ouro(s)")
    return aprovados, ouro


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords",      required=True)
    parser.add_argument("--output",        required=True)
    parser.add_argument("--country",       default="BR")
    parser.add_argument("--platform",      default="facebook")
    parser.add_argument("--active-min",    type=int, default=7,  dest="active_min")
    parser.add_argument("--collation-min", type=int, default=10, dest="collation_min")
    parser.add_argument("--max-results",   type=int, default=50, dest="max_results")
    args = parser.parse_args()

    api_key = os.getenv("SCRAPECREATORS_API_KEY")
    if not api_key:
        print("[ERRO] SCRAPECREATORS_API_KEY não encontrada.")
        sys.exit(1)

    ads, ouro = scrape_meta_ads(
        api_key=api_key, keywords=args.keywords,
        country=args.country, platform=args.platform,
        active_duration_min=args.active_min,
        collation_count_min=args.collation_min,
        max_results=args.max_results
    )

    if not ads:
        print("[AVISO] Nenhum anúncio passou pelos filtros.")
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump([], f)
        sys.exit(0)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)
    print(f"[scraper] ✓ {len(ads)} anúncios salvos em '{args.output}'")

    if ouro:
        print(f"\n{'='*55}")
        print(f"[OPORTUNIDADE OURO] {len(ouro)} anúncio(s) com métricas explosivas!")
        for ad in ouro:
            d = ad.get("active_duration") or ad.get("days_active", "?")
            c = ad.get("collation_count") or ad.get("engagement", "?")
            print(f"  → {ad.get('page_name','?')} | {d}d ativo | {c} engaj")
        print("AÇÃO: Notifique @Alavanca CEO com tag [OPORTUNIDADE OURO].")
        print('='*55)
        ouro_file = args.output.replace(".json", "_ouro.json")
        with open(ouro_file, "w", encoding="utf-8") as f:
            json.dump(ouro, f, ensure_ascii=False, indent=2)
        print(f"[scraper] Ouros salvos em '{ouro_file}'")


if __name__ == "__main__":
    main()
