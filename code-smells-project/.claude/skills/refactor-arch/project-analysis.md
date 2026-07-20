# Project Analysis Heuristics

Use este documento para identificar automaticamente o stack e a arquitetura do projeto em análise.

---

## 1. Detecção de Linguagem

| Sinal | Linguagem |
|---|---|
| Arquivos `.py` presentes | Python |
| Arquivos `.js` presentes (sem `.ts`) | JavaScript |
| Arquivos `.ts` presentes | TypeScript |
| Shebang `#!/usr/bin/env python` | Python |
| Sintaxe `def funcao():` | Python |
| Sintaxe `function foo() {` ou `const foo = () =>` | JavaScript/TypeScript |

**Procedimento:** Liste todas as extensões de arquivo no projeto. A extensão dominante determina a linguagem.

---

## 2. Detecção de Framework

### Python
| Sinal | Framework |
|---|---|
| `from flask import Flask` | Flask |
| `import flask` | Flask |
| `Flask(__name__)` | Flask |
| `from django.db import models` | Django |
| `from fastapi import FastAPI` | FastAPI |
| `flask` em `requirements.txt` | Flask |
| `django` em `requirements.txt` | Django |
| `fastapi` em `requirements.txt` | FastAPI |

### Node.js
| Sinal | Framework |
|---|---|
| `require('express')` ou `import express` | Express |
| `require('fastify')` | Fastify |
| `require('koa')` | Koa |
| `"express"` em `package.json` dependencies | Express |

**Procedimento:**
1. Se existir `requirements.txt`, leia seu conteúdo
2. Se existir `package.json`, leia o campo `dependencies`
3. Inspecione o arquivo de entry point (app.py, index.js, server.js, main.py)

---

## 3. Detecção de Banco de Dados

### Python
| Sinal | Banco |
|---|---|
| `import sqlite3` | SQLite (raw) |
| `from sqlalchemy` | SQLAlchemy (ORM) |
| `from flask_sqlalchemy` | SQLite/PostgreSQL via Flask-SQLAlchemy |
| `psycopg2` | PostgreSQL |
| `pymysql` ou `mysql-connector` | MySQL |
| `pymongo` | MongoDB |
| `sqlite` em connection string | SQLite |
| `postgresql` em connection string | PostgreSQL |

### Node.js
| Sinal | Banco |
|---|---|
| `require('sqlite3')` | SQLite |
| `require('mysql2')` ou `require('mysql')` | MySQL |
| `require('pg')` | PostgreSQL |
| `require('mongoose')` | MongoDB |
| `require('sequelize')` | SQL via Sequelize ORM |

---

## 4. Detecção de Arquitetura Atual

### Monolítico (sem camadas)
- Tudo em 1-2 arquivos
- Rotas, lógica de negócio e acesso a dados misturados no mesmo arquivo
- Arquivo principal >150 linhas com múltiplas responsabilidades

### MVC Parcial
- Existe separação em diretórios (models/, routes/, controllers/) mas...
- Lógica de negócio ainda presente em routes
- SQL em controllers
- Configuração hardcoded em múltiplos lugares

### MVC Completo
- models/ contém apenas mapeamento de dados
- controllers/ contém apenas lógica de negócio
- routes/ contém apenas roteamento HTTP
- config/ contém configurações via env vars
- middlewares/ centralizados

**Procedimento:**
1. Liste a estrutura de diretórios
2. Abra o arquivo de entry point e verifique quantas responsabilidades ele tem
3. Verifique se existem subdiretórios por camada (models, controllers, routes)
4. Classifique como: Monolítico, MVC Parcial, ou MVC Completo

---

## 5. Detecção de Domínio

Identifique o domínio da aplicação pelas palavras-chave em nomes de funções, rotas e tabelas:

| Palavras-chave | Domínio |
|---|---|
| `produto`, `pedido`, `carrinho`, `cliente`, `payment`, `cart`, `order`, `product` | E-commerce |
| `task`, `tarefa`, `categoria`, `prioridade`, `status`, `due_date` | Task Manager |
| `course`, `lesson`, `enrollment`, `student`, `instructor`, `module` | LMS (Learning Management) |
| `user`, `auth`, `login`, `register` | Autenticação (domínio secundário) |

---

## 6. Estimativa de Complexidade

Após identificar o stack, estime a complexidade:

| Métrica | Como medir |
|---|---|
| Número de arquivos | `find . -name "*.py" -o -name "*.js"` (excluindo node_modules e venv) |
| Linhas de código | Somar linhas dos arquivos encontrados |
| Número de endpoints | Contar `@app.route` (Flask) ou `app.get/post/put/delete` (Express) |
| Número de entidades | Contar classes em models ou tabelas CREATE TABLE |
