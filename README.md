# Painel de Estoque

Sistema web de controle de estoque para pequenos negócios, feito com **Django** e **PostgreSQL**. Permite cadastrar produtos, registrar entradas e saídas, acompanhar o histórico de movimentações e receber alertas de estoque baixo, com acesso separado por perfil de usuário.

## Funcionalidades

- **Login** com usuário e senha (senhas armazenadas com hash pelo sistema de autenticação do Django)
- **Início** com resumo do estoque: produtos ativos, valor total em estoque, itens abaixo do mínimo e últimas movimentações
- **Produtos**: lista com busca por nome ou SKU e destaque em vermelho para itens abaixo do estoque mínimo
- **Cadastro, edição e desativação de produtos** direto no painel (apenas perfil Administrador)
- **Movimentação de estoque**: entradas e saídas atualizam o saldo automaticamente
- **Histórico** de movimentações com filtro por produto e por tipo
- **Painel administrativo** do Django em português, para gestão de usuários e dados

## Regras de negócio

- Uma **saída maior que o saldo disponível é bloqueada**, e o saldo nunca fica negativo.
- Cada movimentação roda dentro de uma **transação** com bloqueio da linha do produto, evitando que duas saídas simultâneas deixem o saldo inconsistente.
- O **histórico é imutável**: movimentações não podem ser editadas nem apagadas. Um erro de lançamento se corrige com uma movimentação contrária.
- O **saldo não é editável na mão**. Ele só muda por movimentação, para o histórico sempre bater com o estoque.
- Ao cadastrar um produto com **quantidade inicial** maior que zero, o sistema registra automaticamente uma Entrada no histórico.
- Produtos são **desativados** em vez de apagados, preservando o histórico de movimentações.

## Perfis de acesso

| Perfil | Produtos | Movimentações |
|---|---|---|
| **Funcionário** | apenas visualizar | visualizar e registrar entradas e saídas |
| **Administrador** | visualizar, cadastrar, editar e desativar | visualizar e registrar |

Os perfis são criados por um comando próprio (`criar_perfis`), o que torna a configuração reproduzível em qualquer ambiente.

## Tecnologias

- Python
- Django
- PostgreSQL (driver `psycopg`)
- Bootstrap 5 (via CDN)
- `python-dotenv` para variáveis de ambiente

## Estrutura do projeto

```
painel-estoque-django/
├── manage.py
├── requirements.txt
├── config/                  # configurações do projeto
└── estoque/
    ├── models.py            # Produto e Movimentacao (com a regra de saldo)
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── management/commands/
    │   └── criar_perfis.py  # cria os grupos Administrador e Funcionário
    └── templates/
```

## Como rodar localmente

**Requisitos:** Python 3.12 ou superior, PostgreSQL 16 ou superior e Git.

1. Clone o repositório e entre na pasta:

```bash
git clone https://github.com/Luckfield5/Estoque-com-interface
cd painel-estoque-django
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie o banco de dados no PostgreSQL:

```sql
CREATE DATABASE painel_estoque;
```

5. Crie um arquivo `.env` na raiz do projeto, ao lado do `manage.py`:

```
DB_NAME=painel_estoque
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=5432
```

6. Crie as tabelas, os perfis e o administrador:

```bash
python manage.py migrate
python manage.py criar_perfis
python manage.py createsuperuser
```

7. Inicie o servidor:

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para o painel e `http://127.0.0.1:8000/admin/` para a administração.

Para criar usuários de cada perfil, entre no `/admin/`, vá em **Usuários**, marque **Membro da equipe** e escolha o grupo **Funcionário** ou **Administrador**.

## Capturas de tela

Adicione aqui imagens do projeto (por exemplo, em uma pasta `docs/`):

- Tela de início
- Lista de produtos com alerta de estoque baixo
- Formulário de movimentação com o erro de saldo insuficiente
- Histórico de movimentações

## Sobre o projeto

Projeto desenvolvido por **Lucas** para praticar desenvolvimento back end com Python, modelagem de banco de dados relacional e regras de negócio com controle de concorrência.