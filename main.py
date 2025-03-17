from estrategia_banco import EstrategiaSQL, EstrategiaNoSQL, EstrategiaNoSQL_ComTransacao
from contexto_banco import ContextoBanco

if __name__ == "__main__":
    # Parâmetros: números das contas e saldos iniciais
    conta_a = 1
    conta_b = 2
    saldo_inicial_a = 100.0
    saldo_inicial_b = 100.0
    valor_transferencia = 50.0

    # Teste de Isolamento

    print("=== Usando SQL (PostgreSQL) ===")
    estrategia_sql = EstrategiaSQL()
    contexto_sql = ContextoBanco(estrategia_sql)
    contexto_sql.executar(conta_a, saldo_inicial_a, conta_b, saldo_inicial_b, valor_transferencia)

    print("\n=== Usando NoSQL (MongoDB) ===")
    estrategia_nosql = EstrategiaNoSQL()
    contexto_nosql = ContextoBanco(estrategia_nosql)
    contexto_nosql.executar(conta_a, saldo_inicial_a, conta_b, saldo_inicial_b, valor_transferencia)

    print("\n=== Usando NoSQL com Transação (MongoDB) ===")
    estrategia_nosql_transacao = EstrategiaNoSQL_ComTransacao()
    contexto_nosql_transacao = ContextoBanco(estrategia_nosql_transacao)
    contexto_nosql_transacao.executar(conta_a, saldo_inicial_a, conta_b, saldo_inicial_b, valor_transferencia)
