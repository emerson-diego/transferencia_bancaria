import psycopg2
from pymongo import MongoClient
import time

from estrategia_banco import EstrategiaBancoDados



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

