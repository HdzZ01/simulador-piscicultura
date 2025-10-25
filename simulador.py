import os
import psycopg2
import numpy as np  # Usado para simulações numéricas (Seno e Ruído)
import random
from datetime import datetime

# --- CONFIGURAÇÕES GLOBAIS DA SIMULAÇÃO ---
# Parâmetros de ML: Chance de uma crise de O2 (1 em 500 execuções)
CHANCE_CRISE_O2 = 500 

def obter_ids_dos_tanques(cursor):
    """
    Passo 1: Lê o banco de dados e retorna uma lista de todos
    os IDs da tabela 'tanques'.
    """
    print("Buscando IDs dos tanques cadastrados...")
    cursor.execute("SELECT id_tanque FROM tanques")
    # Usa list comprehension para extrair os IDs
    # (ex: [(1,), (2,)] vira [1, 2])
    lista_ids = [item[0] for item in cursor.fetchall()]
    print(f"Encontrados {len(lista_ids)} tanques.")
    return lista_ids

def simular_leitura_para_tanque(id_tanque):
    """
    Passo 2: O cérebro da simulação.
    Gera uma única leitura realista para um tanque,
    garantindo que todos os tipos numéricos sejam floats nativos do Python.
    """
    
    agora = datetime.now()
    hora_decimal = agora.hour + agora.minute / 60
    
    # --- Simulação de Temperatura (Ciclo Diário) ---
    temp_base = 26.0 
    temp_variacao = 1.5 * np.sin((hora_decimal - 10) * (2 * np.pi / 24))
    temp_ruido = np.random.normal(0, 0.2)
    # CORREÇÃO: Converte o resultado do numpy para float nativo
    temperatura = float(round(temp_base + temp_variacao + temp_ruido, 2))
    
    # --- Simulação de pH ---
    ph_base = 7.9
    ph_variacao_temp = -0.05 * temp_variacao
    ph_ruido = np.random.normal(0, 0.05)
    # CORREÇÃO: Converte para float nativo
    ph = float(round(ph_base + ph_variacao_temp + ph_ruido, 2))

    # --- Simulação de Oxigênio (O Ponto Crítico do ML) ---
    if random.randint(1, CHANCE_CRISE_O2) == 1:
        # CRISE!
        # CORREÇÃO: Converte para float nativo
        oxigenio = float(round(np.random.uniform(2.5, 3.5), 2))
    else:
        # Normal
        o2_base = 7.0
        o2_variacao_temp = -0.5 * temp_variacao
        o2_ruido = np.random.normal(0, 0.1)
        # CORREÇÃO: Converte para float nativo
        oxigenio = float(round(o2_base + o2_variacao_temp + o2_ruido, 2))

    # --- Simulação do Ciclo de Nitrogênio ---
    # CORREÇÃO: Converte todos os resultados (x3) para float nativo
    amonia = float(round(np.abs(np.random.normal(0.01, 0.05)), 3))
    nitrito = float(round(np.abs(np.random.normal(0.005, 0.01)), 3))
    nitrato = float(round(np.abs(np.random.normal(2.0, 0.5)), 2))
    
    # --- Simulação de Parâmetros de "Tampão" ---
    # CORREÇÃO: Converte todos os resultados (x3) para float nativo
    alcalinidade = float(round(np.random.normal(80, 5), 2))
    condutividade_ec = float(round(np.random.normal(300, 15), 2))
    transparencia = float(round(np.random.normal(40, 3), 2))
    
    # Retorna uma tupla na ordem EXATA da tabela 'leituras_iot'
    return (
        id_tanque,
        agora, # O timestamp
        temperatura,
        ph,
        oxigenio,
        amonia,
        nitrito,
        nitrato,
        alcalinidade,
        condutividade_ec,
        transparencia
    )

def main():
    """
    Função principal que orquestra todo o processo.
    """
    print(f"--- Iniciando ciclo de simulação: {datetime.now()} ---")
    
    # 1. Obter a URL de conexão
    DB_URL = os.environ.get('DB_URL_NEON')
    if not DB_URL:
        raise ValueError("Variável de ambiente DB_URL_NEON não definida.")
    
    conn = None
    try:
        # 2. Conectar ao Banco
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # 3. Ler os tanques existentes
        lista_ids_tanques = obter_ids_dos_tanques(cursor)
        
        if not lista_ids_tanques:
            print("AVISO: Nenhum tanque encontrado no banco de dados.")
            return

        # 4. Gerar a simulação
        print("Gerando novas leituras simuladas...")
        leituras_para_inserir = []
        for id_tanque in lista_ids_tanques:
            nova_leitura = simular_leitura_para_tanque(id_tanque)
            leituras_para_inserir.append(nova_leitura)
            
        # 5. Inserir os novos dados (DML)
        sql_insert = """
            INSERT INTO leituras_iot 
            (id_tanque, "timestamp", temperatura, ph, oxigenio_dissolvido, 
             amonia, nitrito, nitrato, alcalinidade, condutividade_ec, transparencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        print(f"Inserindo {len(leituras_para_inserir)} novas leituras no banco Neon...")
        cursor.executemany(sql_insert, leituras_para_inserir)
        
        # 6. Salvar (Commit)
        conn.commit()
        
        print(f"Sucesso! {cursor.rowcount} leituras inseridas.")

    except Exception as e:
        print(f"ERRO: A simulação falhou.")
        print(e)
        if conn:
            conn.rollback() # Desfaz as mudanças em caso de erro
            
    finally:
        # 7. Fechar a conexão
        if conn:
            conn.close()
            print("Conexão fechada.")

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    main()