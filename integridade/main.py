
from estrategia_banco import  EstrategiaSQLIntegridade, EstrategiaNoSQLIntegridade
from contexto_banco import  ContextoIntegridade

if __name__ == "__main__":
    saldo_inicial_a = 100.0
    saldo_inicial_b = 100.0
    


    # Teste de Integridade/Consistência SALDO NEGATIVO
    """
    print("\n=== Teste de Integridade/Consistência ===")

    valor_transferencia = 60.0

    print("\n>> Usando SQL Integridade")
    estrategia_sql_integridade = EstrategiaSQLIntegridade()
    contexto_integridade_sql = ContextoIntegridade(estrategia_sql_integridade)
    contexto_integridade_sql.executar_teste_saldo_negativo(saldo_inicial_a, saldo_inicial_b, valor_transferencia)

    print("\n>> Usando NoSQL Integridade")
    estrategia_nosql_integridade = EstrategiaNoSQLIntegridade()
    contexto_integridade_nosql = ContextoIntegridade(estrategia_nosql_integridade)
    contexto_integridade_nosql.executar_teste_saldo_negativo(saldo_inicial_a, saldo_inicial_b, valor_transferencia)
    """

    # Teste de Integridade/Consistência REGISTRO ORFÃO
    #"""
    valor_transferencia = 50.0
    print("\n=== Teste de Integridade/Consistência ===")

    print("\n>> Usando SQL Integridade")
    estrategia_sql_integridade = EstrategiaSQLIntegridade()
    contexto_integridade_sql = ContextoIntegridade(estrategia_sql_integridade)
    contexto_integridade_sql.executar_teste_registro_orfao(saldo_inicial_a, saldo_inicial_b, valor_transferencia)

    print("\n>> Usando NoSQL Integridade")
    estrategia_nosql_integridade = EstrategiaNoSQLIntegridade()
    contexto_integridade_nosql = ContextoIntegridade(estrategia_nosql_integridade)
    contexto_integridade_nosql.executar_teste_registro_orfao(saldo_inicial_a, saldo_inicial_b, valor_transferencia)
    #"""
