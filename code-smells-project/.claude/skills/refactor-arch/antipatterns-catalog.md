# Anti-Patterns Catalog

Catálogo de 17 anti-patterns arquiteturais e de segurança para detecção automática durante auditoria.

Para cada anti-pattern, verifique o sinal de detecção no código fonte. Registre cada ocorrência com arquivo e linha.

---

## CRITICAL

### 1. God Class / God Method
**Severidade:** CRITICAL
**Descrição:** Uma única classe ou arquivo concentra múltiplas responsabilidades de domínios distintos (acesso a dados + lógica de negócio + roteamento HTTP).

**Sinais de Detecção:**
- Arquivo com mais de 200 linhas de código
- Funções de domínios diferentes no mesmo arquivo (ex: `get_produtos`, `processar_pedido`, `autenticar_usuario` na mesma classe)
- Classe com mais de 5 métodos públicos de responsabilidades distintas
- Arquivo contendo tanto `CREATE TABLE` / ORM model quanto handlers de rota HTTP

**Impacto:** Impossibilidade de testar unidades isoladas, alto acoplamento, dificulta manutenção e extensão.

---

### 2. Hardcoded Credentials
**Severidade:** CRITICAL
**Descrição:** Credenciais, chaves de API ou segredos embutidos diretamente no código fonte.

**Sinais de Detecção:**
- Regex: `(password|passwd|secret|key|token|apikey|api_key)\s*=\s*["'][^"']{4,}["']`
- Variáveis com valores literais de senha (ex: `db_password = "admin123"`)
- Chaves de API hardcoded (ex: `payment_key = "pk_live_abc123"`)
- Credenciais de email hardcoded (ex: `smtp_user = "app@gmail.com"`, `smtp_pass = "senha123"`)
- SECRET_KEY Flask hardcoded (ex: `app.secret_key = "minha-chave-secreta"`)
- Credenciais no código de teste ou configuração

**Impacto:** Exposição de segredos em repositórios públicos, comprometimento de sistemas de produção.

---

### 3. SQL Injection
**Severidade:** CRITICAL
**Descrição:** Dados do usuário inseridos diretamente em queries SQL por concatenação de strings.

**Sinais de Detecção:**
- `cursor.execute("SELECT ... WHERE ... = " + variavel)`
- `cursor.execute("SELECT ... WHERE ... = '%s'" % variavel)`
- `cursor.execute(f"SELECT ... WHERE ... = '{variavel}'")`
- F-strings ou concatenação em qualquer chamada `execute()`, `query()`, `raw()`
- Parâmetros de request usados em queries sem sanitização

**Impacto:** Exposição total do banco de dados, deleção/modificação de dados, bypass de autenticação.

---

### 4. Arbitrary SQL Execution
**Severidade:** CRITICAL
**Descrição:** Endpoint que recebe uma query SQL como parâmetro e a executa diretamente.

**Sinais de Detecção:**
- Rota que recebe `request.args.get('query')` ou `request.json.get('sql')` e passa para `cursor.execute()`
- Endpoint `/admin/query`, `/api/sql`, `/debug/execute` ou similar
- `cursor.execute(request.args.get('...'))`
- Sem autenticação no endpoint de execução SQL

**Impacto:** Comprometimento total do banco de dados e potencialmente do servidor.

---

### 5. Plaintext / Weak Password Storage
**Severidade:** CRITICAL
**Descrição:** Senhas armazenadas em texto puro ou com algoritmo criptograficamente fraco.

**Sinais de Detecção:**
- `hashlib.md5(password` — MD5 é reversível com rainbow tables
- `hashlib.sha1(password` — SHA1 é insuficiente para senhas
- Função `badCrypto()` ou similar com implementação customizada fraca
- Ausência de `bcrypt`, `werkzeug.security.generate_password_hash`, `argon2`
- Senha comparada diretamente: `if user.password == password:`
- Senha salva sem hash: `user.password = request.json['password']`

**Impacto:** Comprometimento de todas as contas em caso de vazamento do banco de dados.

---

### 6. Fake / Missing Authentication
**Severidade:** CRITICAL
**Descrição:** Tokens de autenticação falsos, previsíveis, ou ausência completa de autenticação.

**Sinais de Detecção:**
- `'fake-jwt-token-' + str(user.id)` ou similar
- Token construído com ID do usuário sem assinatura criptográfica
- `token = "hardcoded-token-value"`
- Rotas críticas sem decorator `@login_required`, `@jwt_required`, ou middleware de auth
- Endpoint `/admin/*` sem verificação de autenticação

**Impacto:** Acesso não autorizado a dados e funções privilegiadas.

---

## HIGH

### 7. No Authentication on Sensitive Routes
**Severidade:** HIGH
**Descrição:** Rotas sensíveis (admin, financeiro, dados de usuários) sem qualquer camada de autenticação.

**Sinais de Detecção:**
- Rotas com `/admin/`, `/financial/`, `/report/` sem middleware de auth
- Em Flask: `@app.route('/admin/...')` sem `@login_required` antes
- Em Express: `app.get('/admin/...', handler)` sem middleware de autenticação
- Endpoint que retorna dados de múltiplos usuários sem validar quem está solicitando

**Impacto:** Exposição de dados sensíveis a qualquer usuário ou atacante.

---

### 8. Business Logic in Controller / Route Handler
**Severidade:** HIGH
**Descrição:** Handler de rota HTTP contém lógica de negócio complexa em vez de apenas delegar para serviços/controllers.

**Sinais de Detecção:**
- Handler de rota com mais de 50 linhas de código
- Queries SQL diretamente no handler de rota (sem passar por model/controller)
- Cálculos de negócio, validações de domínio, ou transformações complexas dentro do handler
- Múltiplos `if/else` de regras de negócio no handler

**Impacto:** Impossibilidade de reusar lógica, dificuldade de testar, violação do Single Responsibility Principle.

---

### 9. Callback Hell (Node.js)
**Severidade:** HIGH
**Descrição:** Callbacks aninhados em múltiplos níveis criando estrutura de "pirâmide da perdição".

**Sinais de Detecção:**
- 3 ou mais níveis de callbacks aninhados
- Estrutura visual de pirâmide/indentação crescente em operações assíncronas
- `db.query(..., function(err, result) { db.query(..., function(err2, result2) { ... }) })`
- Tratamento de erro repetido em cada nível do callback

**Impacto:** Código ilegível, difícil de manter, propenso a erros de tratamento de exceção.

---

## MEDIUM

### 10. N+1 Query Problem
**Severidade:** MEDIUM
**Descrição:** Uma query inicial retorna N registros e, para cada registro, uma nova query é executada — resultando em N+1 queries totais.

**Sinais de Detecção:**
- Query ou `find()` dentro de loop `for`, `forEach`, `map`
- `for item in items: db.execute("SELECT ... WHERE id = ?", (item.related_id,))`
- `items.forEach(item => db.query("SELECT ... WHERE id = ?", [item.relatedId]))`
- ORM lazy loading em loop (ex: `for task in tasks: task.user.name`)

**Impacto:** Degradação exponencial de performance com crescimento de dados.

---

### 11. Code Duplication
**Severidade:** MEDIUM
**Descrição:** Bloco de lógica idêntico ou quase idêntico presente em 2 ou mais funções/arquivos.

**Sinais de Detecção:**
- Funções com nomes similares e corpos quase idênticos (ex: `get_pedidos_usuario` vs `get_todos_pedidos`)
- Mesma query SQL escrita em múltiplos lugares
- Mesma lógica de validação repetida em diferentes handlers
- Cálculo de campo derivado (ex: `is_overdue = due_date < datetime.now()`) em 3+ lugares

**Impacto:** Inconsistências quando a lógica precisa ser atualizada, manutenção difícil.

---

### 12. Missing Input Validation
**Severidade:** MEDIUM
**Descrição:** Dados recebidos do usuário (request body, query params, path params) usados sem validação de tipo, formato ou presença.

**Sinais de Detecção:**
- `request.json.get('campo')` usado diretamente sem verificar tipo ou presença
- `request.args.get('id')` passado para query sem converter para inteiro
- Ausência de validação de schema (marshmallow, pydantic, joi, zod)
- Campos opcionais usados como se fossem obrigatórios sem verificação de None/undefined

**Impacto:** Erros inesperados em produção, potencial para injeção de dados malformados.

---

### 13. Deprecated / Insecure APIs
**Severidade:** MEDIUM
**Descrição:** Uso de APIs ou bibliotecas obsoletas, inseguras, ou não recomendadas.

**Sinais de Detecção:**
- `hashlib.md5()` ou `hashlib.sha1()` para hashing de senhas (use bcrypt/argon2)
- `new Buffer()` no Node.js (use `Buffer.from()`)
- `sqlite3` sem ORM para operações CRUD (propenso a SQL Injection)
- Algoritmo de criptografia customizado ("roll your own crypto")
- `Math.random()` para geração de tokens de segurança (use `secrets.token_hex` ou `crypto.randomBytes`)
- `eval()` com input do usuário

**Impacto:** Vulnerabilidades de segurança conhecidas, comportamento imprevisível.

---

## LOW

### 14. Debug / Print Logging
**Severidade:** LOW
**Descrição:** Código de debug ativo em ambiente de produção ou uso de print/console.log para logging.

**Sinais de Detecção:**
- `DEBUG = True` em configuração de produção (Flask)
- `app.run(debug=True)` sem verificação de ambiente
- `print()` usado como mecanismo de logging (Python)
- `console.log()` com dados sensíveis ou em paths de produção (Node.js)
- Dados de cartão de crédito, senhas ou tokens em logs
- `app.run(host='0.0.0.0', debug=True)` — expõe debugger Werkzeug com execução de código

**Impacto:** Exposição de debugger interativo (permite execução de código arbitrário), vazamento de informações sensíveis em logs.

---

### 15. Magic Numbers
**Severidade:** LOW
**Descrição:** Valores numéricos ou de string literais sem nome simbólico espalhados pelo código, tornando o propósito do valor opaco.

**Sinais de Detecção:**
- Comparações com literais numéricos sem constante nomeada: `if status == 2:`, `if role == 3:`
- Limites e thresholds sem nome: `if len(items) > 100:`, `if price > 9999:`
- Timeouts e delays hardcoded: `time.sleep(5)`, `setTimeout(fn, 3000)`
- Códigos HTTP como literais inline: `return jsonify(...), 422` sem constante `HTTP_UNPROCESSABLE_ENTITY`
- Multiplicadores de negócio sem explicação: `total = subtotal * 1.15` (sem indicar que 1.15 é taxa de imposto)

**Impacto:** Código difícil de entender e manter; alterar o valor exige busca global no código em vez de mudar uma constante.

---

### 16. Nomenclatura Ruim de Variáveis e Funções
**Severidade:** LOW
**Descrição:** Variáveis, funções ou parâmetros com nomes genéricos, abreviados ou sem semântica, dificultando a leitura e compreensão do código.

**Sinais de Detecção:**
- Variáveis de uma ou duas letras fora de loops de índice: `d`, `x`, `n`, `tmp`, `res`
- Abreviações sem contexto: `usr` em vez de `user`, `dt` em vez de `date`, `prd` em vez de `product`
- Funções com nomes genéricos: `process()`, `handle()`, `do_stuff()`, `run()`
- Variáveis booleanas sem prefixo `is_`, `has_`, `can_`: `active = True` em vez de `is_active = True`
- Parâmetros nomeados `data`, `info`, `obj` sem indicar o tipo ou domínio

**Impacto:** Reduz legibilidade, aumenta o tempo de onboarding de novos desenvolvedores e facilita introdução de bugs por mal-entendimento do propósito.

---

### 17. Código Morto / Código Comentado
**Severidade:** LOW
**Descrição:** Funções, variáveis ou blocos de código não utilizados, ou código comentado que permanece no codebase sem propósito documentado.

**Sinais de Detecção:**
- Funções definidas mas nunca chamadas em nenhum ponto do projeto
- Imports não utilizados: `import os` ou `const _ = require('lodash')` sem uso posterior
- Blocos de código comentado com `#` ou `//` com mais de 3 linhas sem explicação
- Variáveis declaradas e atribuídas mas nunca lidas: `result = fetch_data()` sem uso de `result`
- Parâmetros de função recebidos mas ignorados no corpo da função

**Impacto:** Polui o codebase, gera confusão sobre o que está ativo, aumenta o esforço de leitura e pode mascarar código legado que deveria ter sido removido.
