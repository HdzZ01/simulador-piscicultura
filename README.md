# Simulador de Dados para Piscicultura

Este script automatiza a geração de dados realistas para monitoramento de tanques de peixes, integrando simulações matemáticas com persistência em banco de dados PostgreSQL (Neon DB).

### O que o projeto faz:
* **Modelagem de Dados Realistas:** Utiliza NumPy para simular ciclos diários de temperatura (senoide) e variações correlacionadas de pH e Oxigênio.
* **Simulação de Eventos Críticos:** Inclui lógica de probabilidade para gerar "crises de oxigênio", simulando situações de risco real para análise de dados posterior.
* **Integração Cloud:** Conexão robusta com banco de dados remoto usando Psycopg2, com tratamento de exceções e controle de transações (commit/rollback).

### Tecnologias Utilizadas:
* **Python:** Lógica principal e orquestração.
* **NumPy:** Geração de distribuições normais e ruídos estatísticos para simular sensores reais.
* **PostgreSQL (Neon):** Armazenamento estruturado das leituras de IoT.
* **Dotenv/OS:** Gerenciamento seguro de variáveis de ambiente para credenciais de banco de dados.

### Como funciona:
O script lê os IDs dos tanques cadastrados no banco, gera uma leitura simulada para cada um com base no horário atual e insere os dados via `executemany` para garantir performance.
