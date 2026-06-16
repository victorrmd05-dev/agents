# Resumo: Integração Hermes Agent + Paperclip na VPS

## Objetivo
Conectar o Hermes Agent ao Paperclip para que o Hermes seja:
1. **Assistente pessoal** via Telegram e terminal — dando ordens ao Paperclip
2. **Agente SEO** dentro do Paperclip — executando tarefas automaticamente

## Arquitetura Final
```
Você (Telegram / terminal)
    ↓ fala com Hermes
Hermes Agent (VPS - rodando 24/7)
    ↓ gerencia via MCP (a instalar)
Paperclip (paperclip.zedocarro.cloud)
    ↓ empresa virtual
Alavancaai — empresa com agentes
```

---

## Infraestrutura

### VPS
- **Provedor:** Hostinger
- **Plano:** KVM 2
- **OS:** Ubuntu 24.04 LTS
- **IP:** 76.13.238.201
- **SSH:** `ssh root@76.13.238.201`
- **Disco:** 96GB (12% usado)
- **RAM:** 7.8GB

### Domínios (Cloudflare Tunnel)
- `coolify.zedocarro.cloud` → Coolify painel (porta 8000)
- `paperclip.zedocarro.cloud` → Paperclip (porta 3100)

---

## O Que Está Instalado e Funcionando

### ✅ Coolify v4.1.0
- Rodando em `coolify.zedocarro.cloud`
- Containers: coolify, coolify-proxy (Traefik), coolify-db, coolify-redis, coolify-sentinel, coolify-realtime
- **NÃO mexer nesses containers**

### ✅ Hermes Agent v0.14.0
- Instalado em `/app/hermes-agent/`
- Executável: `/app/hermes-agent/hermes` (script Python)
- Symlink global: `/usr/local/bin/hermes`
- Config em: `/root/.hermes/`
- **Provider:** OpenRouter
- **Modelo:** `nvidia/nemotron-3-super-120b-a12b:free` (gratuito)
- **Telegram:** Bot configurado (`Hermesclip`) — funcionando ✅
- **Gateway:** Rodando como serviço do sistema (PID 1689001)
- **Comando para iniciar chat:** `hermes chat`
- **Comando para ver gateway:** `hermes gateway`

### ✅ Paperclip
- Rodando em `paperclip.zedocarro.cloud`
- Container: `paperclip-l48w8euycfksd3zhgcqm6ikp` (nome pode mudar após restart)
- Deploy via Coolify → projeto "Alavancaai" → service "paperclip"
- Volume de dados: `l48w8euycfksd3zhgcqm6ikp_paperclip-data` (nome pode mudar)
- **Status:** Rodando mas precisa de onboard/conta

---

## Estado Atual (Onde Paramos)

### Paperclip
- Volume foi apagado e recriado limpo (resolveu problema de permissão PostgreSQL)
- Rodando e acessível em `paperclip.zedocarro.cloud`
- Mostra "Instance setup required" — precisa de onboard + conta admin
- **Próximo passo:** Rodar onboard e criar conta
- Comando onboard:
```bash
docker exec -it $(docker ps | grep paperclip | awk '{print $1}') pnpm paperclipai onboard
```
- Comando para gerar link de convite (após onboard):
```bash
docker exec -it $(docker ps | grep paperclip | awk '{print $1}') pnpm paperclipai auth bootstrap-ceo
```

### Hermes como Agente no Paperclip
- **Problema em aberto:** O Paperclip tenta rodar `hermes` mas o container não tem Python/dependências
- **Tentativas feitas:** cp do executável, pip install (sem pip no container), montar volume Python
- **Solução pendente:** Configurar o adapter do Hermes no Paperclip apontando para o executável correto
- O Paperclip tem suporte nativo ao Hermes Agent (aparece na lista de adapters)
- No onboarding foi selecionado **Hermes Agent** como tipo de agente

---

## Variáveis de Ambiente do Paperclip (no Coolify)
```
BETTER_AUTH_SECRET=925c25141142c4671727762588d671f442b147d73e55c78041800d092426360f
OPENAI_API_KEY=sk-proj-... (configurado)
OPENROUTER_API_KEY=sk-or-v1-... (configurado)
PAPERCLIP_PUBLIC_URL=https://paperclip.zedocarro.cloud
PAPERCLIP_ALLOWED_HOSTNAMES=paperclip.zedocarro.cloud
PAPERCLIP_DEPLOYMENT_MODE=authenticated
PAPERCLIP_DEPLOYMENT_EXPOSURE=private
HOST=0.0.0.0
PAPERCLIP_HOME=/paperclip
```

### Compose atual (no Coolify):
```yaml
services:
  paperclip:
    image: ghcr.io/paperclipai/paperclip:latest
    environment:
      HOST: "0.0.0.0"
      PAPERCLIP_HOME: "/paperclip"
      PAPERCLIP_DEPLOYMENT_MODE: "authenticated"
      PAPERCLIP_DEPLOYMENT_EXPOSURE: "private"
      PAPERCLIP_PUBLIC_URL: "https://paperclip.zedocarro.cloud"
      PAPERCLIP_ALLOWED_HOSTNAMES: "paperclip.zedocarro.cloud"
      BETTER_AUTH_SECRET: "${BETTER_AUTH_SECRET}"
      OPENAI_API_KEY: "${OPENAI_API_KEY}"
      OPENROUTER_API_KEY: "${OPENROUTER_API_KEY}"
    volumes:
      - paperclip-data:/paperclip
      - /app/hermes-agent:/app/hermes-agent
      - /root/.hermes:/root/.hermes
      - /usr/local/lib/python3.12:/usr/local/lib/python3.12
    ports:
      - "3100:3100"

volumes:
  paperclip-data:
```

---

## Hermes Config
```
Settings: /root/.hermes/config.yaml
API Keys: /root/.hermes/.env
Data: /root/.hermes/cron/, sessions/, logs/
Provider: OpenRouter
Model: nvidia/nemotron-3-super-120b-a12b:free
Telegram: configurado e funcionando
```

---

## Próximos Passos (em ordem)

1. **Completar onboard do Paperclip** (Quickstart desta vez)
2. **Gerar link de convite** e criar conta admin
3. **Criar empresa "Alavancaai"** no Paperclip
4. **Configurar agente Hermes** — resolver o problema de Python dentro do container
5. **Instalar MCP do Paperclip no Hermes** — para o Hermes controlar o Paperclip via terminal/Telegram
6. **Testar fluxo completo:** Você → Telegram → Hermes → Paperclip → Hermes executa tarefa

---

## Problemas Conhecidos e Soluções

### Hermes não encontrado no container Paperclip
- **Causa:** Container Node.js sem Python
- **Tentativa 1:** `docker cp` do symlink — falhou (symlink vazio)
- **Tentativa 2:** `pip install` no container — falhou (sem pip)
- **Tentativa 3:** Montar volume Python — causou problema de permissão no PostgreSQL
- **Solução a tentar:** Configurar adapter do Hermes no Paperclip com caminho absoluto + montar apenas as dependências necessárias

### Permissão PostgreSQL corrompida
- **Causa:** `chmod 777` aplicado ao volume inteiro
- **Solução:** Apagar volume e recriar — **JÁ RESOLVIDO**

### Hermes modelo OpenAI Codex (sessão expirada)
- **Causa:** Provider `openai-codex` usa sessão do browser do ChatGPT
- **Solução:** Trocado para OpenRouter — **JÁ RESOLVIDO**

---

## Comandos Úteis

```bash
# Ver containers rodando
docker ps

# Logs do Paperclip
docker logs $(docker ps | grep paperclip | awk '{print $1}') --tail 50

# Entrar no container Paperclip
docker exec -it $(docker ps | grep paperclip | awk '{print $1}') bash

# Onboard Paperclip
docker exec -it $(docker ps | grep paperclip | awk '{print $1}') pnpm paperclipai onboard

# Gerar link de convite admin
docker exec -it $(docker ps | grep paperclip | awk '{print $1}') pnpm paperclipai auth bootstrap-ceo

# Hermes chat
hermes chat

# Hermes gateway (mensageria Telegram)
hermes gateway

# Ver status do gateway
hermes gateway status

# Verificar saúde do Hermes
hermes doctor
```

---

## Empresa no Paperclip
- **Nome:** Alavancaai
- **Foco:** Vendas de produtos físicos (dropshipping) e digitais (infoprodutos)
- **Agente criado:** CEO (Hermes Agent)
- **Projeto:** Onboarding
- **Primeira tarefa criada:** "Estruturar o workflow inicial de criação de ofertas e páginas de vendas"
