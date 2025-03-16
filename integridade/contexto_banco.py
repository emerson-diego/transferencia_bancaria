
from estrategia_banco import EstrategiaBancoDados

class ContextoIntegridade:
    def __init__(self, estrategia):
        self.estrategia = estrategia
        self.estrategia.conectar()

    def executar_teste_saldo_negativo(self, saldo_conta_a, saldo_conta_b, valor_transferencia):
        # Criação das contas com integridade
        self.estrategia.criar_contas(saldo_conta_a, saldo_conta_b)
        # Tenta realizar transferência que pode levar a saldo negativo
        self.estrategia.transferir_saldo_negativo(valor_transferencia)
        # Exibe os saldos atuais
        try:
            saldos = self.estrategia.obter_saldos()
            print("Saldos após teste de integridade:", saldos)
        except Exception as e:
            print("Erro ao obter saldos:", e)

    
    def executar_teste_registro_orfao(self, saldo_conta_a, saldo_conta_b, valor_transferencia):
        # Criação das contas com integridade
        self.estrategia.criar_contas(saldo_conta_a, saldo_conta_b)
        # Tenta realizar transferência que pode levar a saldo negativo
        self.estrategia.transferir_orfao(valor_transferencia)
        # Exibe os saldos atuais
        try:
            saldos = self.estrategia.obter_saldos()
            print("Saldos após teste de integridade:", saldos)
        except Exception as e:
            print("Erro ao obter saldos:", e)
