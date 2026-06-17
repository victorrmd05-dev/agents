#!/usr/bin/env python3
"""
Minerador — Classificação por IA e Gravação no Supabase
Uso: python scripts/process_and_save_offer.py --input raw_drop.json --category Dropshipping [--keywords "nicho beleza"]
"""
import os
import json
import argparse
import sys
import requests
from supabase import create_client, Client

PROMPT_CLASSIFICACAO = """Você é um analista de performance em marketing direto brasileiro.
Analise este anúncio e retorne APENAS um JSON válido, sem texto adicional, sem markdown.

DADOS DO ANÚNCIO:
{dados_anuncio}

CATEGORIA: {categoria}
NICHO DA BUSCA: {nicho}

Retorne exatamente este JSON:
{{
  "categoria_ia": "<Dropshipping | InfoProduto | Mentoria | Software | Outro>",
  "score_escala": <número de 0.0 a 10.0>,
  "notas_ia": "<2-3 frases: o que está escalando, qual o ângulo da oferta, sinal de durabilidade>"
}}

CRITÉRIOS DE SCORE:
- 9-10: Ativo há mais de 20 dias, promessa forte e específica, engajamento alto
- 7-8: Ativo 7-15 dias, ângulo claro, produto com demanda real
- 5-6: Promessa genérica mas produto real, ou números medianos
- 3-4: Oferta vaga, saturada ou instável
- 0-2: Sem identidade, sem promessa, puro spam"""


def classificar_com_ia(ad_data: dict, categoria: str, nicho: str, api_key: str) -> dict:
    campos = {
        "page_name":       ad_data.get("page_name") or ad_data.get("advertiser_name", ""),
        "body":            ad_data.get("ad_creative_body") or ad_data.get("body") or ad_data.get("text", ""),
        "title":           ad_data.get("ad_creative_link_title") or ad_data.get("title", ""),
        "description":     ad_data.get("ad_creative_link_description") or ad_data.get("description", ""),
        "active_duration": ad_data.get("active_duration") or ad_data.get("days_active", 0),
        "collation_count": ad_data.get("collation_count") or ad_data.get("engagement", 0),
    }

    prompt = PROMPT_CLASSIFICACAO.format(
        dados_anuncio=json.dumps(campos, ensure_ascii=False, indent=2),
        categoria=categoria,
        nicho=nicho or "Geral"
    )

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=20
        )
        r.raise_for_status()
        content = r.json()["content"][0]["text"].strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        return json.loads(content.strip())

    except json.JSONDecodeError:
        print("  [AVISO] JSON inválido da IA — fallback aplicado.")
        return {"categoria_ia": categoria, "score_escala": 5.0, "notas_ia": "Classificação falhou — revisão manual."}
    except Exception as e:
        print(f"  [AVISO] Erro na IA: {e}")
        return {"categoria_ia": categoria, "score_escala": None, "notas_ia": f"Erro: {str(e)[:100]}"}


def salvar_no_supabase(registros: list) -> int:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("[ERRO] SUPABASE_URL ou SUPABASE_KEY ausentes.")
        return 0
    try:
        sb = create_client(url, key)
        res = sb.table("ads_minerados").insert(registros).execute()
        return len(res.data) if res.data else 0
    except Exception as e:
        print(f"[ERRO Supabase] {e}")
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",     required=True)
    parser.add_argument("--category",  required=True)
    parser.add_argument("--keywords",  default="")
    parser.add_argument("--score-min", type=float, default=4.0, dest="score_min")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("[ERRO] SUPABASE_URL e SUPABASE_KEY são obrigatórios.")
        sys.exit(1)
    if not api_key:
        print("[AVISO] ANTHROPIC_API_KEY ausente — scores ficarão NULL.")

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            ads = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] '{args.input}' não encontrado.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERRO] JSON inválido: {e}")
        sys.exit(1)

    if not ads:
        print("[AVISO] Nenhum anúncio para processar.")
        sys.exit(0)

    nicho = args.keywords
    print(f"[processor] {len(ads)} anúncios | categoria: {args.category} | nicho: {nicho or 'Geral'} | score mín: {args.score_min}")

    registros   = []
    descartados = 0
    ouro_count  = 0

    for i, ad in enumerate(ads, 1):
        nome    = (ad.get("page_name") or ad.get("advertiser_name") or "sem nome")[:50]
        eh_ouro = ad.get("_ouro", False)
        print(f"\n[{i}/{len(ads)}] {nome}{' ⭐ OURO' if eh_ouro else ''}")

        if api_key:
            cl = classificar_com_ia(ad, args.category, nicho, api_key)
        else:
            cl = {"categoria_ia": args.category, "score_escala": None, "notas_ia": None}

        score = cl.get("score_escala")

        # Ouro nunca é descartado por score baixo
        if score is not None and score < args.score_min and not eh_ouro:
            print(f"  → Descartado | score {score} < {args.score_min}")
            descartados += 1
            continue

        notas = cl.get("notas_ia") or ""
        if eh_ouro:
            ouro_count += 1
            notas = f"[OPORTUNIDADE OURO] {notas}".strip()

        registros.append({
            "query_busca":  nicho or args.category,
            "raw_json":     ad,
            "categoria_ia": cl.get("categoria_ia"),
            "score_escala": score,
            "notas_ia":     notas,
        })
        print(f"  → Score: {score} | {cl.get('categoria_ia')}")

    print(f"\n[processor] Aprovados: {len(registros)} | Descartados: {descartados} | Ouro: {ouro_count}")

    if not registros:
        print("[processor] Nenhum anúncio aprovado.")
        sys.exit(0)

    inseridos = salvar_no_supabase(registros)
    print(f"[processor] ✓ {inseridos} registros gravados no Supabase.")

    if ouro_count:
        print(f"\n{'='*55}")
        print(f"[OPORTUNIDADE OURO] {ouro_count} oferta(s) marcadas no Supabase.")
        print("AÇÃO OBRIGATÓRIA: Notifique @Alavanca CEO com tag [OPORTUNIDADE OURO].")
        print('='*55)


if __name__ == "__main__":
    main()
