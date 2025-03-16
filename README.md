Protótipo de Transferência Bancária: SQL vs NoSQL
Este protótipo demonstra a superioridade dos bancos de dados SQL em garantir a integridade dos dados em transações críticas, em comparação aos bancos NoSQL. Usamos uma simulação de transferência bancária com falha intencional para evidenciar como o SQL preserva a consistência automaticamente, enquanto o NoSQL exige esforço adicional para lidar com inconsistências.

Pré-requisitos
Docker e Docker Compose

Docker
Docker Compose
Python 3.8+

Download Python
uv (gerenciador de pacotes Python)

Repositório do uv
Dica: Se você ainda não possui o uv instalado, instale-o globalmente utilizando o pip:

bash
Copiar
pip install uv
Passos para Rodar a Aplicação
1. Subir os Bancos de Dados com Docker Compose
No diretório raiz do projeto, certifique-se de que o arquivo docker-compose.yml contém a seguinte configuração:

yaml
Copiar
version: '3.8'

services:
  postgres:
    image: postgres:latest
    environment:
      POSTGRES_USER: usuario
      POSTGRES_PASSWORD: senha
      POSTGRES_DB: banco_db
    ports:
      - "5432:5432"

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
Em seguida, execute o comando abaixo para iniciar os containers:

bash
Copiar
docker-compose up -d
Isso iniciará dois containers:

PostgreSQL (SQL) na porta 5432
MongoDB (NoSQL) na porta 27017
Observação: Verifique se os containers estão ativos com:

bash
Copiar
docker ps
2. Criar o Ambiente Virtual com uv
No diretório do projeto, crie um ambiente virtual utilizando o uv:

bash
Copiar
uv venv
3. Instalar as Dependências Python
Com o ambiente virtual criado, instale as bibliotecas necessárias (psycopg2-binary e pymongo) utilizando o uv:

bash
Copiar
uv pip install psycopg2-binary pymongo
4. Ativar o Ambiente Virtual
Ative o ambiente virtual criado para que os comandos e pacotes sejam executados corretamente:

Linux/macOS:

bash
Copiar
source .venv/bin/activate
Windows:

bash
Copiar
.venv\Scripts\activate
5. Executar a Aplicação
Com o ambiente virtual ativo e os containers do Docker rodando, execute o script principal da aplicação. Supondo que o arquivo principal seja bank_transfer.py, execute:

bash
Copiar
uv run python bank_transfer.py
Você deverá ver a execução dos testes para ambas as estratégias (SQL e NoSQL) com os saldos iniciais e após a tentativa de transferência com falha simulada.

