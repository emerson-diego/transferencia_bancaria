from abc import abstractmethod


# Interface Strategy com números de contas como parâmetro
class EstrategiaBancoDados():
    @abstractmethod
    def conectar(self):
        pass

    @abstractmethod
    def criar_contas(self, conta_a, saldo_conta_a, conta_b, saldo_conta_b):
        pass

    @abstractmethod
    def transferir(self, conta_a, conta_b, valor):
        pass

    @abstractmethod
    def obter_saldos(self, conta_a, conta_b):
        pass

