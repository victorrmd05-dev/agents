# Alavanca AI - Agentes

Este repositório contém a configuração e a estrutura organizacional dos agentes de Inteligência Artificial do ecossistema **Alavanca AI**, orquestrados via Paperclip.

## Sobre o Projeto

A Alavanca AI é uma agência impulsionada por agentes de IA que colaboram entre si para realizar tarefas complexas, desde a mineração de produtos até a criação de campanhas de tráfego pago. A comunicação e passagem de bastão entre os agentes acontece através de um banco de dados Supabase compartilhado e integrado nativamente.

## Estrutura Organizacional dos Agentes

Abaixo estão os agentes configurados no ecossistema e suas principais responsabilidades:

- **00 - CEO (Paperclip)**: O orquestrador principal de todo o ecossistema do Paperclip.
- **01 - CEO Alavanca AI**: Líder da agência de inteligência artificial. Fornece diretrizes e aprovações de alto nível (representando o usuário do sistema).
- **02 - CTO**: Diretor de infraestrutura técnica. Responsável pelo gerenciamento de chaves de API, configuração das conexões e suporte técnico aos outros agentes.
- **03 - Minerador**: Focado na mineração de infoprodutos e ofertas validadas através da análise de dados usando scrapers de meta ads. Alimenta o banco de dados inicial (`workflow_mineracao`).
- **04 - Copywriting**: Especialista em escrita persuasiva. Responsável por criar as copys para as páginas de vendas e anúncios, usando os produtos aprovados no dashboard. Escreve os resultados na tabela `workflow_copywriting`.
- **05 - Revisor**: Controle de qualidade. Responsável pela revisão rigorosa das copys geradas, garantindo aderência aos padrões da Alavanca AI e validando a versão final junto com o CEO.
- **06 - Designer-Webmaster**: Especialista em criação web. Responsável por traduzir as copys aprovadas no desenvolvimento e deploy de landing pages funcionais e de alta conversão.
- **07 - Video-Maker**: Especialista em criativos visuais. Usa a API do Higgsfield para criação de vídeos para os anúncios com base nos ganchos emocionais da copy aprovada.
- **08 - Gestor-Meta-Ads**: Especialista em tráfego pago. Responsável pela gestão, criação e otimização das campanhas de tráfego utilizando os criativos e as landing pages produzidas pelos outros agentes.

## Arquitetura e Fluxo

Para visualizar visualmente o fluxo e a hierarquia da equipe de agentes, consulte o arquivo local `Hierarquia_agents.canvas` no seu Obsidian.

## Como começar

1. Certifique-se de configurar suas chaves de API no arquivo `.env` (este arquivo é ignorado pelo `.gitignore` para manter suas credenciais seguras).
2. Explore a pasta `agents/` para ver as definições de cada agente e a pasta `skills/` para visualizar as habilidades disponíveis para a equipe.

## 🛠️ Padrões de Comunicação (Agent References)
- **Padrão de Referência de Agentes**: SEMPRE referencie outros agentes nos arquivos `agent.md` e `SKILL.md` usando a notação estrita `[@NomeDoAgente](agent://nome-do-agente)`. (Exemplo: `[@Minerador](agent://minerador)` ou `[@Alavanca CEO](agent://alavanca-ceo)`). NUNCA use caminhos locais de arquivo.
    

    