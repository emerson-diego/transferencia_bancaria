from abc import ABC, abstractmethod
import psycopg2
from pymongo import MongoClient
import time

# Interface Strategy com números de contas como parâmetro
class EstrategiaBancoDados(ABC):
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

    def criar_contas(self, conta_a, saldo_conta_a, conta_b, saldo_conta_b):
        inicio = time.perf_counter()
        self.cursor.execute("DROP TABLE IF EXISTS contas")
        # Alterado: definir 'id' como INTEGER PRIMARY KEY para permitir inserção manual
        self.cursor.execute("CREATE TABLE contas (id INTEGER PRIMARY KEY, saldo FLOAT)")
        self.cursor.execute(
            "INSERT INTO contas (id, saldo) VALUES (%s, %s), (%s, %s)",
            (conta_a, saldo_conta_a, conta_b, saldo_conta_b)
        )
        self.conexao.commit()
        fim = time.perf_counter()
        print("Tempo de inserção SQL: {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, conta_a, conta_b, valor):
        try:
            self.cursor.execute("BEGIN")
            self.cursor.execute("UPDATE contas SET saldo = saldo - %s WHERE id = %s", (valor, conta_a))
            # Simula falha após debitar a conta 'conta_a'
            raise Exception("Falha simulada durante a transferência")
            self.cursor.execute("UPDATE contas SET saldo = saldo + %s WHERE id = %s", (valor, conta_b))
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print(f"Erro na transferência SQL: {e}")

    def obter_saldos(self, conta_a, conta_b):
        self.cursor.execute("SELECT id, saldo FROM contas WHERE id IN (%s, %s)", (conta_a, conta_b))
        resultados = self.cursor.fetchall()
        # Organiza os saldos para retornar na ordem: [saldo da conta_a, saldo da conta_b]
        saldos_dict = {registro[0]: registro[1] for registro in resultados}
        return [saldos_dict.get(conta_a), saldos_dict.get(conta_b)]

# Estratégia NoSQL (MongoDB) - sem transação
class EstrategiaNoSQL(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("localhost", 27017)
        self.banco_dados = self.cliente.bank_db
        self.contas = self.banco_dados.contas

    def criar_contas(self, conta_a, saldo_conta_a, conta_b, saldo_conta_b):
        inicio = time.perf_counter()
        self.contas.drop()  # Limpa a coleção
        self.contas.insert_many([
            {"_id": conta_a, "saldo": saldo_conta_a},
            {"_id": conta_b, "saldo": saldo_conta_b}
        ])
        fim = time.perf_counter()
        print("Tempo de inserção NoSQL: {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, conta_a, conta_b, valor):
        try:
            self.contas.update_one({"_id": conta_a}, {"$inc": {"saldo": -valor}})
            # Simula falha após debitar a conta 'conta_a'
            raise Exception("Falha simulada durante a transferência")
            self.contas.update_one({"_id": conta_b}, {"$inc": {"saldo": valor}})
        except Exception as e:
            print(f"Erro na transferência NoSQL: {e}")

    def obter_saldos(self, conta_a, conta_b):
        conta_a_doc = self.contas.find_one({"_id": conta_a})
        conta_b_doc = self.contas.find_one({"_id": conta_b})
        return [conta_a_doc["saldo"], conta_b_doc["saldo"]]

# Estratégia NoSQL (MongoDB) - com transação
class EstrategiaNoSQL_ComTransacao(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("localhost", 27017)
        self.banco_dados = self.cliente.bank_db
        self.contas = self.banco_dados.contas

    def criar_contas(self, conta_a, saldo_conta_a, conta_b, saldo_conta_b):
        inicio = time.perf_counter()
        self.contas.drop()  # Limpa a coleção
        self.contas.insert_many([
            {"_id": conta_a, "saldo": saldo_conta_a},
            {"_id": conta_b, "saldo": saldo_conta_b}
        ])
        fim = time.perf_counter()
        print("Tempo de inserção NoSQL (com transação): {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, conta_a, conta_b, valor):
        with self.cliente.start_session() as session:
            try:
                with session.start_transaction():
                    self.contas.update_one(
                        {"_id": conta_a},
                        {"$inc": {"saldo": -valor}},
                        session=session
                    )
                    # Simula falha após debitar a conta 'conta_a'
                    raise Exception("Falha simulada durante a transferência")
                    self.contas.update_one(
                        {"_id": conta_b},
                        {"$inc": {"saldo": valor}},
                        session=session
                    )
            except Exception as e:
                print(f"Erro na transferência NoSQL (com transação): {e}")

    def obter_saldos(self, conta_a, conta_b):
        conta_a_doc = self.contas.find_one({"_id": conta_a})
        conta_b_doc = self.contas.find_one({"_id": conta_b})
        return [conta_a_doc["saldo"], conta_b_doc["saldo"]]
