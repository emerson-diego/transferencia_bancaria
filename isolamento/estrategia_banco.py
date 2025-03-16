from abc import ABC, abstractmethod
import psycopg2
from pymongo import MongoClient
import time

# Interface Strategy
class EstrategiaBancoDados(ABC):
    @abstractmethod
    def conectar(self):
        pass

    @abstractmethod
    def criar_contas(self, saldo_conta_a, saldo_conta_b):
        pass

    @abstractmethod
    def transferir(self, valor):
        pass

    @abstractmethod
    def obter_saldos(self):
        pass

# Estratégia SQL (PostgreSQL)
class EstrategiaSQL(EstrategiaBancoDados):
    def conectar(self):
        self.conexao = psycopg2.connect(
            dbname="banco_db",
            user="usuario",
            password="senha",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conexao.cursor()

    def criar_contas(self, saldo_conta_a, saldo_conta_b):
        inicio = time.perf_counter()  
        self.cursor.execute("DROP TABLE IF EXISTS contas")
        self.cursor.execute("CREATE TABLE contas (id SERIAL PRIMARY KEY, saldo FLOAT)")
        self.cursor.execute("INSERT INTO contas (saldo) VALUES (%s), (%s)", (saldo_conta_a, saldo_conta_b))
        self.conexao.commit()
        fim = time.perf_counter()  
        print("Tempo de inserção SQL: {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, valor):
        try:
            self.cursor.execute("BEGIN")
            self.cursor.execute("UPDATE contas SET saldo = saldo - %s WHERE id = 1", (valor,))
            # Simula falha após debitar da conta A
            raise Exception("Falha simulada durante a transferência")
            self.cursor.execute("UPDATE contas SET saldo = saldo + %s WHERE id = 2", (valor,))
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print(f"Erro na transferência SQL: {e}")

    def obter_saldos(self):
        self.cursor.execute("SELECT saldo FROM contas ORDER BY id")
        saldos = self.cursor.fetchall()
        return [saldo[0] for saldo in saldos]

# Estratégia NoSQL (MongoDB) - sem transação
class EstrategiaNoSQL(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("localhost", 27017)
        self.banco_dados = self.cliente.bank_db
        self.contas = self.banco_dados.contas

    def criar_contas(self, saldo_conta_a, saldo_conta_b):
        inicio = time.perf_counter()  # Marca o início da operação
        self.contas.drop()  # Limpa a coleção
        self.contas.insert_many([
            {"_id": 1, "saldo": saldo_conta_a},
            {"_id": 2, "saldo": saldo_conta_b}
        ])
        fim = time.perf_counter()  # Marca o fim da operação
        print("Tempo de inserção NoSQL: {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, valor):
        try:
            self.contas.update_one({"_id": 1}, {"$inc": {"saldo": -valor}})
            # Simula falha após debitar da conta A
            raise Exception("Falha simulada durante a transferência")
            self.contas.update_one({"_id": 2}, {"$inc": {"saldo": valor}})
        except Exception as e:
            print(f"Erro na transferência NoSQL: {e}")

    def obter_saldos(self):
        conta_a = self.contas.find_one({"_id": 1})
        conta_b = self.contas.find_one({"_id": 2})
        return [conta_a["saldo"], conta_b["saldo"]]

# Estratégia NoSQL (MongoDB) - com transação
class EstrategiaNoSQL_ComTransacao(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("localhost", 27017)
        self.banco_dados = self.cliente.bank_db
        self.contas = self.banco_dados.contas

    def criar_contas(self, saldo_conta_a, saldo_conta_b):
        inicio = time.perf_counter()  # Marca o início da operação
        self.contas.drop()  # Limpa a coleção
        self.contas.insert_many([
            {"_id": 1, "saldo": saldo_conta_a},
            {"_id": 2, "saldo": saldo_conta_b}
        ])
        fim = time.perf_counter()  # Marca o fim da operação
        print("Tempo de inserção NoSQL (com transação): {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, valor):
        with self.cliente.start_session() as session:
            try:
                with session.start_transaction():
                    self.contas.update_one(
                        {"_id": 1},
                        {"$inc": {"saldo": -valor}},
                        session=session
                    )
                    # Simula falha após debitar da conta A
                    raise Exception("Falha simulada durante a transferência")
                    self.contas.update_one(
                        {"_id": 2},
                        {"$inc": {"saldo": valor}},
                        session=session
                    )
            except Exception as e:
                print(f"Erro na transferência NoSQL (com transação): {e}")

    def obter_saldos(self):
        conta_a = self.contas.find_one({"_id": 1})
        conta_b = self.contas.find_one({"_id": 2})
        return [conta_a["saldo"], conta_b["saldo"]]
