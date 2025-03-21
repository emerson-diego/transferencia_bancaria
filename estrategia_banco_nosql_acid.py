
import psycopg2
from pymongo import MongoClient
import time

from estrategia_banco import EstrategiaBancoDados

# Estratégia NoSQL (MongoDB) - com transação (multi-documentos)
class EstrategiaNoSQL_ACID(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
        #self.cliente = MongoClient("localhost", 27017)
        self.banco_dados = self.cliente.bank_db

    def criar_contas(self, conta_a, saldo_conta_a, conta_b, saldo_conta_b):
        inicio = time.perf_counter()
        # Dropar coleções se existirem
        self.banco_dados.drop_collection("contas")
        self.banco_dados.drop_collection("transacoes")

        # Criar coleção 'contas' com validação de esquema para garantir saldo >= 0
        self.banco_dados.create_collection("contas", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["_id", "saldo"],
                "properties": {
                    "_id": {"bsonType": "int"},
                    "saldo": {"bsonType": ["int", "double"], "minimum": 0}
                }
            }
        })
        self.contas = self.banco_dados.contas

        # Criar coleção 'transacoes' com validação básica
        self.banco_dados.create_collection("transacoes", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["conta_id", "descricao", "valor"],
                "properties": {
                    "conta_id": {"bsonType": "int"},
                    "descricao": {"bsonType": "string"},
                    "valor": {"bsonType": ["int", "double"]}
                }
            }
        })
        self.transacoes = self.banco_dados.transacoes

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
                    # Verificar se ambas as contas existem
                    doc_origem = self.contas.find_one({"_id": conta_a}, session=session)
                    doc_destino = self.contas.find_one({"_id": conta_b}, session=session)
                    if not doc_origem:
                        raise Exception(f"Conta {conta_a} não existe.")
                    if not doc_destino:
                        raise Exception(f"Conta {conta_b} não existe.")

                    # Verificar saldo suficiente na conta de origem
                    #if doc_origem["saldo"] < valor:
                    #    raise Exception("Saldo insuficiente na conta de origem.")

                    # Atualizar conta de origem e registrar transação de débito
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

                    # Atualizar conta de destino e registrar transação de crédito
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
        return [doc_a["saldo"] if doc_a else None, doc_b["saldo"] if doc_b else None]
