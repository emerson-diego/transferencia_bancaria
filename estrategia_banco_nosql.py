from abc import ABC, abstractmethod
import psycopg2
from pymongo import MongoClient
import time

from estrategia_banco import EstrategiaBancoDados


# Estratégia NoSQL (MongoDB) - sem transação (modo normal)
class EstrategiaNoSQL(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
        self.cliente = MongoClient("mongodb://localhost:27017/")
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
        print("Tempo de inserção NoSQL: {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, conta_a, conta_b, valor, simular_falha=False):
        try:

            self.contas.update_one({"_id": conta_a}, {"$inc": {"saldo": -valor}})

            self.transacoes.insert_one({
                "conta_id": conta_a,
                "descricao": "Débito",
                "valor": valor
            })

            if simular_falha:
                raise Exception("Falha simulada durante a transferência")

            self.contas.update_one({"_id": conta_b}, {"$inc": {"saldo": valor}})

            self.transacoes.insert_one({
                "conta_id": conta_b,
                "descricao": "Crédito",
                "valor": valor
            })
        except Exception as e:
            print(f"Erro na transferência NoSQL: {e}")

    def obter_saldos(self, conta_a, conta_b):
        doc_a = self.contas.find_one({"_id": conta_a})
        doc_b = self.contas.find_one({"_id": conta_b})
        return [doc_a["saldo"], doc_b["saldo"]]
