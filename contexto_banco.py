from estrategia_banco import EstrategiaBancoDados

# Contexto que utiliza a estratégia de banco de dados
class ContextoBanco:

    def __init__(self, estrategia: EstrategiaBancoDados):
        self.estrategia = estrategia

    def executar(self, conta_a, conta_b, valor_transferencia, simular_falha=False):
        conta_a_inicial = 1
        conta_b_inicial = 2
        conta_a_saldo_inicial = 100.0
        conta_b_saldo_inicial = 100.0

        self.estrategia.conectar()
        self.estrategia.criar_contas(conta_a_inicial, conta_a_saldo_inicial, conta_b_inicial, conta_b_saldo_inicial)
        print("Saldos iniciais:", self.estrategia.obter_saldos(conta_a_inicial, conta_b_inicial))
        
        self.estrategia.transferir(conta_a, conta_b, valor_transferencia, simular_falha)
        print("Saldos após transferência:", self.estrategia.obter_saldos(conta_a_inicial, conta_b_inicial))
