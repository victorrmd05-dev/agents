#!/usr/bin/env python3
"""
Minerador — Processamento, Classificação por IA e Gravação no Supabase
Uso: python scripts/process_and_save_offer.py --input raw_drop.json --category Dropshipping
"""
import os
import json
import argparse
import sys
import requests
from supabase import create_client, Client

# ─── Prompt de classificação ─────────────────────────────────────────────────
PROMPT_CLASSIFICACAO = """Você é um analista sênior de performance em marketing digital brasileiro.
Analise este anúncio e retorne APENAS um JSON válido, sem texto adicional, sem markdown.

DADOS DO ANÚNCIO:
{dados_anuncio}

CATEGORIA DE MERCADO: {categoria}

Retorne exatamente este JSON:
{{
  "categoria_ia": "<categoria detectada: Dropshipping | InfoProduto | Mentoria | Software | Outro>",
  "score_escala": <número de 0.0 a 10.0>,
  "notas_ia": "<análise em 2-3 frases: por que está escalando, qual o mecanismo único, risco de saturação>"
}}

CRITÉRIOS DE SCORE:
- 9-10: Funil completo com VSL + checkout + prova social + anúncio há mais de 20 dias
- 7-8: Anúncio durável (7-15 dias), promessa clara, engajamento alto
- 5-6: Anúncio novo (<7 dias) ou com promessa genérica, mas produto real
- 3-4: Anúncio instável, oferta vaga ou saturada
- 0-2: Lixo — sem funil, sem página, sem diferencial claro"""


def classificar_com_ia(ad_data: dict, categoria: str, api_key_anthropic: str) -> dict:
    """Chama Claude para classificar e pontuar o anúncio."""

    # Extrai só os campos relevantes para não poluir o prompt
    campos_relevantes = {
        "page_name": ad_data.get("page_name") or ad_data.get("advertiser_name", ""),
        "ad_creative_body": ad_data.get("ad_creative_body") or ad_data.get("body") or ad_data.get("text", ""),
        "ad_creative_link_title": ad_data.get("ad_creative_link_title") or ad_data.get("title", ""),
        "ad_creative_link_description": ad_data.get("ad_creative_link_description") or ad_data.get("description", ""),
        "active_duration": ad_data.get("active_duration") or ad_data.get("days_active", 0),
        "collation_count": ad_data.get("collation_count") or ad_data.get("engagement", 0),
        "has_video": bool(ad_data.get("ad_creative_video_url") or ad_data.get("video_url")),
        "has_landing_page": bool(ad_data.get("ad_snapshot_url") or ad_data.get("page_id")),
    }

    prompt = PROMPT_CLASSIFICACAO.format(
        dados_anuncio=json.dumps(campos_relevantes, ensure_ascii=False, indent=2),
        categoria=categoria
    )

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key_anthropic,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",  # rápido e barato para classificação em massa
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=20
        )
        response.raise_for_status()
        content = response.json()["content"][0]["text"].strip()

        # Remove markdown se vier com ```json
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        return json.loads(content.strip())

    except json.JSONDecodeError:
        print(f"[AVISO] IA retornou JSON inválido, usando fallback.")
        return {
            "categoria_ia": categoria,
            "score_escala": 5.0,
            "notas_ia": "Classificação automática falhou — requer revisão manual."
        }
    except Exception as e:
        print(f"[AVISO] Erro na chamada IA: {e}")
        return {
            "categoria_ia": categoria,
            "score_escala": 5.0,
            "notas_ia": f"Erro na classificação: {str(e)[:100]}"
        }


def salvar_no_supabase(registros: list) -> int:
    """Grava lista de registros no Supabase. Retorna quantos foram inseridos."""
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[ERRO] SUPABASE_URL ou SUPABASE_KEY não encontrados.")
        return 0

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("ads_minerados").insert(registros).execute()
        return len(response.data) if response.data else 0
    except Exception as e:
        print(f"[ERRO Supabase] {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Processa anúncios, classifica com IA e salva no Supabase")
    parser.add_argument("--input", required=True, help="JSON de entrada (saída do scraper)")
    parser.add_argument("--category", required=True, help="Categoria: Dropshipping | InfoProduto")
    args = parser.parse_args()

    # ─── Validações de ambiente ───────────────────────────────────────────────
    api_key_anthropic = os.getenv("ANTHROPIC_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[ERRO] SUPABASE_URL e SUPABASE_KEY são obrigatórios.")
        sys.exit(1)

    if not api_key_anthropic:
        print("[AVISO] ANTHROPIC_API_KEY não encontrada. Scores serão NULL — classificação desativada.")

    # ─── Carrega JSON do scraper ──────────────────────────────────────────────
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            ads = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{args.input}' não encontrado.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERRO] JSON inválido em '{args.input}': {e}")
        sys.exit(1)

    if not ads:
        print(f"[AVISO] Nenhum anúncio encontrado em '{args.input}'. Nada a processar.")
        sys.exit(0)

    print(f"[processor] {len(ads)} anúncios para processar | categoria: {args.category}")

    # ─── Processa e classifica cada anúncio ──────────────────────────────────
    registros = []
    for i, ad in enumerate(ads, 1):
        print(f"[processor] {i}/{len(ads)} — {ad.get('page_name') or ad.get('advertiser_name', 'sem nome')[:50]}")

        # Classifica com IA (se API key disponível)
        if api_key_anthropic:
            classificacao = classificar_com_ia(ad, args.category, api_key_anthropic)
        else:
            classificacao = {
                "categoria_ia": args.category,
                "score_escala": None,
                "notas_ia": None
            }

        # Monta registro para o Supabase
        registro = {
            "query_busca": args.category,
            "raw_json": ad,                              # JSON completo do anúncio
            "categoria_ia": classificacao.get("categoria_ia"),
            "score_escala": classificacao.get("score_escala"),
            "notas_ia": classificacao.get("notas_ia"),
        }

        # ─── Filtra lixo por score ────────────────────────────────────────────
        score = classificacao.get("score_escala")
        if score is not None and score < 4.0:
            print(f"  → Score {score} < 4.0 — descartado (lixo)")
            continue

        registros.append(registro)
        print(f"  → Score: {score} | Categoria: {classificacao.get('categoria_ia')}")

    print(f"\n[processor] {len(registros)} anúncios aprovados (score ≥ 4.0) de {len(ads)} processados")

    if not registros:
        print("[processor] Nenhum anúncio passou pelo filtro de qualidade.")
        sys.exit(0)

    # ─── Grava no Supabase ────────────────────────────────────────────────────
    inseridos = salvar_no_supabase(registros)
    print(f"[processor] ✓ {inseridos} registros gravados no Supabase com sucesso.")


if __name__ == "__main__":
    main()
