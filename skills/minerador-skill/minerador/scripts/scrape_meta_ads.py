import os
import requests
import json
import argparse

def is_big_brand(advertiser_name):
    if not advertiser_name:
        return False
    big_brands = ['google', 'netflix', 'amazon', 'apple', 'shopee', 'mercado livre', 'shein']
    name_lower = advertiser_name.lower()
    return any(brand in name_lower for brand in big_brands)

def scrape_meta_ads(api_key, country='BR', platform='facebook', active_duration_min=7, collation_count_min=10, keywords=None, output_file='raw_ads.json'):
    url = "https://api.scrapecreators.com/v1/meta-ads/search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    params = {"country": country, "platform": platform, "active_duration_min": active_duration_min, "collation_count_min": collation_count_min}
    
    if keywords: 
        params["keywords"] = keywords
        
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filtro de grandes marcas
        filtered_ads = []
        raw_ads = data.get('data', [])
        for ad in raw_ads:
            advertiser = ad.get('pageName', '')
            if not is_big_brand(advertiser):
                filtered_ads.append(ad)
                
        # Salva o resultado no json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'data': filtered_ads}, f, ensure_ascii=False, indent=2)
            
        print(f"[SUCESSO] Scraping finalizado! {len(filtered_ads)} anúncios encontrados e salvos em {output_file}.")
        return filtered_ads
        
    except Exception as e:
        print(f"[ERRO] Error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minerador de Anúncios - Scrape Creators API")
    parser.add_argument("--keywords", type=str, help="Palavras-chave para a busca (ex: 'Frete Grátis')", default=None)
    parser.add_argument("--output", type=str, help="Nome do arquivo JSON de saída", default="raw_ads.json")
    
    args = parser.parse_args()
    
    api_key = os.getenv("SCRAPE_CREATORS_API_KEY")
    if not api_key:
        print("[ERRO] Erro: SCRAPE_CREATORS_API_KEY não encontrada no ambiente.")
        exit(1)
        
    scrape_meta_ads(api_key, keywords=args.keywords, output_file=args.output)
