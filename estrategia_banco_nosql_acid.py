
import psycopg2
from pymongo import MongoClient
import time

from estrategia_banco import EstrategiaBancoDados

# Estratégia NoSQL (MongoDB) - com transação (multi-documentos)
class EstrategiaNoSQL_ACID(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("localhost", 27017)
        self.banco_dados = self.cliente.bank_db

        self.contas = self.banco_dados.contas
        self.transacoes = self.banco_dados.transacoes

    def criar_contas(self, conta_a, saldo_conta_a, conta_b, saldo_conta_b):
        inicio = time.perf_counter()
        self.contas.drop()
        self.transacoes.drop()
        self.contas.insert_many([
            {"_id": conta_a, "saldo": saldo_conta_a},
            {"_id": conta_b, "saldo": saldo_conta_b}
        ])
        fim = time.perf_counter()
        print("Tempo de inserção NoSQL (com transação): {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, conta_a, conta_b, valor, simular_falha=False):
        with self.cliente.start_session() as session:
            try:
                with session.start_transaction():

                    self.contas.update_one(
                        {"_id": conta_a},
                        {"$inc": {"saldo": -valor}},
                        session=session
                    )
                    self.transacoes.insert_one(
                        {"conta_id": conta_a, "descricao": "Débito", "valor": valor},
                        session=session
                    )

                    if simular_falha:
                        raise Exception("Falha simulada durante a transferência")
         
                    self.contas.update_one(
                        {"_id": conta_b},
                        {"$inc": {"saldo": valor}},
                        session=session
                    )
                    self.transacoes.insert_one(
                        {"conta_id": conta_b, "descricao": "Crédito", "valor": valor},
                        session=session
                    )

            except Exception as e:
                print(f"Erro na transferência NoSQL (com transação): {e}")

    def obter_saldos(self, conta_a, conta_b):
        doc_a = self.contas.find_one({"_id": conta_a})
        doc_b = self.contas.find_one({"_id": conta_b})
        return [doc_a["saldo"], doc_b["saldo"]]
