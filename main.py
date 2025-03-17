
from contexto_banco import ContextoBanco
from estrategia_banco_nosql import EstrategiaNoSQL
from estrategia_banco_nosql_acid import EstrategiaNoSQL_ACID
from estrategia_banco_sql import EstrategiaSQL

if __name__ == "__main__":

    conta_a = 1
    conta_b = 2
    conta_inexistente = 999
    saldo_inicial_a = 100.0
    saldo_inicial_b = 100.0
    valor_transferencia = 50.0


    print("\n=================== Teste de Atomicidade ==============================")


    print("\n=== Usando SQL (PostgreSQL) ===")
    estrategia_sql = EstrategiaSQL()
    contexto_sql = ContextoBanco(estrategia_sql)
    contexto_sql.executar(conta_a, conta_b, valor_transferencia, simular_falha=True)

    print("\n=== Usando NoSQL (MongoDB) ===")
    estrategia_nosql = EstrategiaNoSQL()
    contexto_nosql = ContextoBanco(estrategia_nosql)
    contexto_nosql.executar(conta_a, conta_b, valor_transferencia, simular_falha=True)

    print("\n=== Usando NoSQL - ACID (MongoDB) ===")
    estrategia_nosql_acid = EstrategiaNoSQL_ACID()
    contexto_nosql_acid = ContextoBanco(estrategia_nosql_acid)
    contexto_nosql_acid.executar(conta_a, conta_b, valor_transferencia, simular_falha=True)

    print("\n\n=================== Teste de Integridade 1 ==============================")

    print("\n=== Usando SQL (PostgreSQL) com falha de integridade ===")
    estrategia_sql = EstrategiaSQL()
    contexto_sql = ContextoBanco(estrategia_sql)
    contexto_sql.executar(conta_a, conta_inexistente, valor_transferencia)

    print("\n=== Usando NoSQL (MongoDB) com simulação de falha de integridade ===")
    estrategia_nosql = EstrategiaNoSQL()
    contexto_nosql = ContextoBanco(estrategia_nosql)
    contexto_nosql.executar(conta_a, conta_inexistente, valor_transferencia)

    print("\n=== Usando NoSQL - ACID (MongoDB) ===")
    estrategia_nosql_acid = EstrategiaNoSQL_ACID()
    contexto_nosql_acid = ContextoBanco(estrategia_nosql_acid)
    contexto_nosql.executar(conta_a, conta_inexistente, valor_transferencia)


    print("\n\n=================== Teste de Integridade 2 ==============================")

    print("\n=== Usando SQL (PostgreSQL) com falha de integridade ===")
    estrategia_sql = EstrategiaSQL()
    contexto_sql = ContextoBanco(estrategia_sql)
    contexto_sql.executar(conta_a, conta_inexistente, 120)

    print("\n=== Usando NoSQL (MongoDB) com simulação de falha de integridade ===")
    estrategia_nosql = EstrategiaNoSQL()
    contexto_nosql = ContextoBanco(estrategia_nosql)
    contexto_nosql.executar(conta_a, conta_inexistente, 120)

    print("\n=== Usando NoSQL - ACID (MongoDB) ===")
    estrategia_nosql_acid = EstrategiaNoSQL_ACID()
    contexto_nosql_acid = ContextoBanco(estrategia_nosql_acid)
    contexto_nosql.executar(conta_a, conta_inexistente, 120)