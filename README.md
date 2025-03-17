# Protótipo de Transferência Bancária: SQL vs NoSQL

Este protótipo demonstra a superioridade dos bancos de dados SQL em garantir a integridade dos dados em transações críticas, em comparação aos bancos NoSQL. Usamos uma simulação de transferência bancária com falha intencional para evidenciar como o SQL preserva a consistência automaticamente, enquanto o NoSQL exige esforço adicional para lidar com inconsistências.

## Pré-requisitos

Para executar este protótipo, você precisará das seguintes ferramentas instaladas:

- **Docker e Docker Compose**
  - [Docker](https://www.docker.com/get-started)
  - [Docker Compose](https://docs.docker.com/compose/install/)
- **Python 3.8+**
  - [Download Python](https://www.python.org/downloads/)
- **uv (gerenciador de pacotes Python)**
  - [Repositório do uv](https://github.com/astral-sh/uv)
  - **Dica:** Se você ainda não possui o uv instalado, instale-o globalmente utilizando o pip:
    ```bash
    pip install uv
    ```

## Passos para Rodar a Aplicação

Siga os passos abaixo para configurar e executar o protótipo:

### 1. Subir os Bancos de Dados com Docker Compose

No diretório raiz do projeto, certifique-se de que o arquivo `docker-compose.yml` contém a seguinte configuração:

```yaml
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
    command: ["mongod", "--replSet", "rs0"]
```

Em seguida, execute o comando abaixo para iniciar os containers:

```bash
docker-compose up -d
```

Isso iniciará dois containers:
PostgreSQL (SQL) na porta 5432

MongoDB (NoSQL) na porta 27017

Observação: Verifique se os containers estão ativos com:

```bash
docker ps
```

Agora, é necessário ativar o modo réplica do mongoDB para que o suporte a transações multi-documentos seja possível

```bash
docker exec -it <id_do_container> mongosh
```

```bash
rs.initiate()
rs.config()
rs.reconfig({
    _id: "rs0",
    members: [
        { _id: 0, host: "localhost:27017" } #altera o replica set para usar localhost
    ]
})
```

### 2. Criar o Ambiente Virtual com uv
No diretório do projeto, crie um ambiente virtual utilizando o uv:

```bash
uv venv
```

### 3. Ativar o Ambiente Virtual
Ative o ambiente virtual criado para garantir que os comandos e pacotes sejam executados corretamente:


Linux/macOS:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```

### 4. Instalar as Dependências Python
Com o ambiente virtual ativo, instale as bibliotecas necessárias (psycopg2-binary e pymongo) utilizando o uv:

```bash
uv pip install psycopg2-binary pymongo
```

### 5. Executar a Aplicação
Com o ambiente virtual ativo e os containers do Docker rodando, execute o script principal da aplicação:

```bash
uv run python main.py
```