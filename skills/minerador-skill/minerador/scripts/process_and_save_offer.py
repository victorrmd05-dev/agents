import os
import json
import argparse
from supabase import create_client, Client

def calculate_score(ad):
    score = 0
    # Score baseado no tempo ativo
    active_days = ad.get("activeDays", 0)
    if active_days >= 30: score += 50
    elif active_days >= 14: score += 30
    elif active_days >= 7: score += 15
    
    # Score baseado no volume (compartilhamentos/versões/colisões)
    collation = ad.get("collationCount", 0)
    if collation >= 50: score += 50
    elif collation >= 20: score += 30
    elif collation >= 10: score += 10
    
    return min(score, 100) # Máximo 100

def process_and_save(input_file):
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY: 
        print("[ERRO] Erro: Credenciais do Supabase não encontradas.")
        return False
        
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        ads = data.get('data', [])
        if not ads:
            print("Nenhum anúncio encontrado no arquivo para processar.")
            return True
            
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        success_count = 0
        for ad in ads:
            score = calculate_score(ad)
            
            offer_data = {
                "id_anuncio": str(ad.get("id", "")),
                "anunciante": ad.get("pageName", ""),
                "page_id": str(ad.get("pageId", "")),
                "ativo_dias": ad.get("activeDays", 0),
                "collation_count": ad.get("collationCount", 0),
                "copy_anuncio": ad.get("body", ""),
                "link_destino": ad.get("ctaUrl", ""),
                "cta_type": ad.get("ctaType", ""),
                "score_matematico": score,
                "categoria_ia": args.category # Adicionado da rodada
            }
            
            try:
                # Upsert ou insert ignorando duplicados (depende da sua PK, estou usando insert)
                supabase.table("ads_minerados").insert(offer_data).execute()
                success_count += 1
            except Exception as e:
                # O anúncio já pode existir
                pass
                
        print(f"[SUCESSO] Sucesso! {success_count}/{len(ads)} anúncios salvos no Supabase com pontuação.")
        return True
        
    except Exception as e:
        print(f"[ERRO] Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processador de Anúncios para o Supabase")
    parser.add_argument("--input", type=str, required=True, help="Arquivo JSON gerado pelo scrape_meta_ads")
    parser.add_argument("--category", type=str, default="Geral", help="Categoria para salvar no banco (ex: Dropshipping, InfoProduto)")
    
    args = parser.parse_args()
    
    process_and_save(args.input)
