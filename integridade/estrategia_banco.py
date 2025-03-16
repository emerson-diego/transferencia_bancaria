from abc import ABC, abstractmethod
import psycopg2
from pymongo import MongoClient
import time

# Interface Strategy
class EstrategiaBancoDados(ABC):
    @abstractmethod
    def conectar(self):
        pass


class EstrategiaSQLIntegridade(EstrategiaBancoDados):
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
        # Cria tabelas com restrições de integridade
        self.cursor.execute("DROP TABLE IF EXISTS transacoes")
        self.cursor.execute("DROP TABLE IF EXISTS contas_integridade")
        self.cursor.execute("""
            CREATE TABLE contas_integridade (
                id SERIAL PRIMARY KEY,
                saldo FLOAT CHECK (saldo >= 0)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE transacoes (
                id SERIAL PRIMARY KEY,
                conta_id INT,
                descricao VARCHAR(100),
                FOREIGN KEY (conta_id) REFERENCES contas_integridade(id)
            )
        """)
        self.cursor.execute("INSERT INTO contas_integridade (saldo) VALUES (%s), (%s)", (saldo_conta_a, saldo_conta_b))
        self.conexao.commit()
        print("Contas integridade SQL criadas com sucesso.")

    def transferir_saldo_negativo(self, valor):
        try:
            self.cursor.execute("BEGIN")
            # Tenta debitar da conta 1 – operação que pode levar a saldo negativo
            self.cursor.execute("UPDATE contas_integridade SET saldo = saldo - %s WHERE id = 1", (valor,))
            # Registra a transação
            self.cursor.execute("INSERT INTO transacoes (conta_id, descricao) VALUES (1, 'Débito')")
            # Tenta debitar novamente da conta 1 para agravar o saldo negativo
            self.cursor.execute("UPDATE contas_integridade SET saldo = saldo - %s WHERE id = 1", (valor,))
            self.cursor.execute("INSERT INTO transacoes (conta_id, descricao) VALUES (1, 'Saldo Negativo')")
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print("Integridade SQL: Operação falhou e foi revertida:", e)

    def transferir_orfao(self, valor):
        try:
            self.cursor.execute("BEGIN")
            # Tenta debitar da conta 1 – operação que pode levar a saldo negativo
            self.cursor.execute("UPDATE contas_integridade SET saldo = saldo - %s WHERE id = 1", (valor,))
            # Registra a transação
            self.cursor.execute("INSERT INTO transacoes (conta_id, descricao) VALUES (1, 'Débito')")
            # Tenta debitar novamente da conta 1 para agravar o saldo negativo
            self.cursor.execute("UPDATE contas_integridade SET saldo = saldo - %s WHERE id = 1", (valor,))
            self.cursor.execute("INSERT INTO transacoes (conta_id, descricao) VALUES (999, 'Registro Órfão')")
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print("Integridade SQL: Operação falhou e foi revertida:", e)


    def obter_saldos(self):
        self.cursor.execute("SELECT saldo FROM contas_integridade ORDER BY id")
        saldos = self.cursor.fetchall()
        return [saldo[0] for saldo in saldos]

# Estratégia NoSQL com "integridade" – sem validação real de integridade
class EstrategiaNoSQLIntegridade(EstrategiaBancoDados):
    def conectar(self):
        self.cliente = MongoClient("localhost", 27017)
        # Usaremos um banco de dados específico para o teste de integridade
        self.banco_dados = self.cliente.bank_db_integridade
        self.contas = self.banco_dados.contas
        self.transacoes = self.banco_dados.transacoes

    def criar_contas(self, saldo_conta_a, saldo_conta_b):
        self.contas.drop()
        self.transacoes.drop()
        self.contas.insert_many([
            {"_id": 1, "saldo": saldo_conta_a},
            {"_id": 2, "saldo": saldo_conta_b}
        ])
        print("Contas integridade NoSQL criadas com sucesso.")
    
    def transferir_saldo_negativo(self, valor):
        try:
            self.contas.update_one({"_id": 1}, {"$inc": {"saldo": -valor}})
            self.transacoes.insert_one({"conta_id": 1, "descricao": "Débito"})
            # Segunda operação para levar a um saldo negativo (o NoSQL não impede)
            self.contas.update_one({"_id": 1}, {"$inc": {"saldo": -valor}})
            self.transacoes.insert_one({"conta_id": 1, "descricao": "Saldo Negativo"})
            print("Transação órfão criada em NoSQL.")
        except Exception as e:
            print("Integridade NoSQL: Erro na transferência:", e)

    def transferir_orfao(self, valor):
        try:
            self.contas.update_one({"_id": 1}, {"$inc": {"saldo": -valor}})
            self.transacoes.insert_one({"conta_id": 1, "descricao": "Débito"})
            # Segunda operação para levar a um saldo negativo (o NoSQL não impede)
            self.contas.update_one({"_id": 1}, {"$inc": {"saldo": -valor}})
            self.transacoes.insert_one({"conta_id": 999, "descricao": "Transação órfão"})
            print("Transação órfão criada em NoSQL.")
        except Exception as e:
            print("Integridade NoSQL: Erro na transferência:", e)


    def obter_saldos(self):
        conta_a = self.contas.find_one({"_id": 1})
        conta_b = self.contas.find_one({"_id": 2})
        return [conta_a["saldo"], conta_b["saldo"]]