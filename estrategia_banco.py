from abc import ABC, abstractmethod
import psycopg2
from pymongo import MongoClient
import time

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

        self.cursor.execute("DROP TABLE IF EXISTS transacoes")
        self.cursor.execute("DROP TABLE IF EXISTS contas")

        self.cursor.execute("""
            CREATE TABLE contas (
                id SERIAL PRIMARY KEY,
                saldo FLOAT CHECK (saldo >= 0)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE transacoes (
                id SERIAL PRIMARY KEY,
                conta_id INT,
                descricao VARCHAR(100),
                valor FLOAT,
                FOREIGN KEY (conta_id) REFERENCES contas(id)                   
            )
        """)

        self.cursor.execute(
            "INSERT INTO contas (id, saldo) VALUES (%s, %s), (%s, %s)",
            (conta_a, saldo_conta_a, conta_b, saldo_conta_b)
        )
        self.conexao.commit()
        fim = time.perf_counter()
        print("Tempo de inserção SQL: {:.2f} ms".format((fim - inicio) * 1000))

    def transferir(self, conta_a, conta_b, valor, simular_falha=False):
        try:
            self.cursor.execute("BEGIN")

            self.cursor.execute(
                "UPDATE contas SET saldo = saldo - %s WHERE id = %s", 
                (valor, conta_a)
            )
            self.cursor.execute(
                "INSERT INTO transacoes (conta_id, descricao, valor) VALUES (%s, 'Débito', %s)", 
                (conta_a, valor)
            )

            if simular_falha:
                raise Exception("Falha simulada durante a transferência")

            self.cursor.execute(
                "UPDATE contas SET saldo = saldo + %s WHERE id = %s", 
                (valor, conta_b)
            )
            self.cursor.execute(
                "INSERT INTO transacoes (conta_id, descricao, valor) VALUES (%s, 'Crédito', %s)", 
                (conta_b, valor)
            )
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print(f"Erro na transferência SQL: {e}")

    def obter_saldos(self, conta_a, conta_b):
        self.cursor.execute(
            "SELECT id, saldo FROM contas WHERE id IN (%s, %s)",
            (conta_a, conta_b)
        )
        resultados = self.cursor.fetchall()
        saldos_dict = {registro[0]: registro[1] for registro in resultados}
        return [saldos_dict.get(conta_a), saldos_dict.get(conta_b)]

# Estratégia NoSQL (MongoDB) - sem transação (modo normal)
class EstrategiaNoSQL(EstrategiaBancoDados):
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

# Estratégia NoSQL (MongoDB) - com transação (multi-documentos)
class EstrategiaNoSQL_ComTransacao(EstrategiaBancoDados):
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
