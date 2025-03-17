from estrategia_banco import EstrategiaBancoDados

# Contexto que utiliza a estratégia de banco de dados
class ContextoBanco:
    def __init__(self, estrategia: EstrategiaBancoDados):
        self.estrategia = estrategia

    def executar(self, conta_a, saldo_inicial_a, conta_b, saldo_inicial_b, valor_transferencia):
        self.estrategia.conectar()
        self.estrategia.criar_contas(conta_a, saldo_inicial_a, conta_b, saldo_inicial_b)
        print("Saldos iniciais:", self.estrategia.obter_saldos(conta_a, conta_b))
        self.estrategia.transferir(conta_a, conta_b, valor_transferencia)
        print("Saldos após transferência:", self.estrategia.obter_saldos(conta_a, conta_b))
