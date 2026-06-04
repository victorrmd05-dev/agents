# Estrutura Organizacional dos Agentes Alavanca AI

Esta é a hierarquia e as responsabilidades dos agentes configurados no Paperclip para o projeto Alavanca AI. A comunicação entre os agentes acontece através de um banco de dados Supabase compartilhado e integrado nativamente.

## 00 - CEO (Paperclip)
O orquestrador principal de todo o ecossistema do Paperclip.

## 01 - CEO Alavanca AI
O CEO e líder da agência de inteligência artificial. Fornece diretrizes e aprovações de alto nível. (Representa o usuário do sistema).

## 02 - CTO
Diretor de infraestrutura técnica, responsável pelo gerenciamento de chaves de API e configuração das conexões. Dá suporte técnico aos outros agentes.

## 03 - Minerador
Focado na mineração de infoprodutos e ofertas validadas através da análise de dados usando scrapers de meta ads. Alimenta o banco de dados inicial (`workflow_mineracao`).

## 04 - Copywriting
Especialista em escrita persuasiva. Responsável por criar as copys para as páginas de vendas e anúncios, usando os produtos aprovados no dashboard. Escreve os resultados na tabela `workflow_copywriting`.

## 05 - Revisor
Controle de qualidade. Responsável pela revisão rigorosa das copys geradas, garantindo aderência aos padrões da Alavanca AI e validando a versão final junto com o CEO Alavanca AI.

## 06 - Designer-Webmaster
Especialista em criação web. Responsável por traduzir as copys aprovadas no desenvolvimento e no deploy de landing pages funcionais e de alta conversão.

## 07 - Video-Maker
Especialista em criativos visuais. Usa a API do Higgsfield para a criação de vídeos para os anúncios com base nos ganchos emocionais da copy aprovada.

## 08 - Gestor-Meta-Ads
Especialista em tráfego pago. Responsável pela gestão, criação e otimização das campanhas de tráfego utilizando os criativos e as landing pages produzidas pelos outros agentes.


![[Hierarquia_agents.canvas]]