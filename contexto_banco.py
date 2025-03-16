
from estrategia_banco import EstrategiaBancoDados


class ContextoBanco:
    def __init__(self, estrategia: EstrategiaBancoDados):
        self.estrategia = estrategia

    def executar(self, saldo_inicial_a, saldo_inicial_b, valor_transferencia):
        self.estrategia.conectar()
        self.estrategia.criar_contas(saldo_inicial_a, saldo_inicial_b)
        print("Saldos iniciais:", self.estrategia.obter_saldos())
        self.estrategia.transferir(valor_transferencia)
        print("Saldos após transferência:", self.estrategia.obter_saldos())
