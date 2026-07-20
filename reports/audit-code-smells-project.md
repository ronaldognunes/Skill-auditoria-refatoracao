```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1 + SQLite (raw)
Files:   4 analyzed | ~784 lines of code

================================
SUMMARY
================================
CRITICAL: 6 | HIGH: 2 | MEDIUM: 4 | LOW: 1
Total:    13 findings

================================
FINDINGS
================================

--- CRITICAL ---

[CRITICAL] God Class / God Method
File:        models.py:1-315
Description: O arquivo models.py possui 315 linhas e concentra funções de 3 domínios distintos
             sem separação: produtos (get_todos_produtos, criar_produto, atualizar_produto,
             deletar_produto, buscar_produtos), usuários (get_todos_usuarios, get_usuario_por_id,
             criar_usuario, login_usuario) e pedidos (criar_pedido, get_pedidos_usuario,
             get_todos_pedidos, relatorio_vendas, atualizar_status_pedido). Além disso,
             controllers.py possui 293 linhas misturando validação, lógica de negócio e
             chamadas HTTP em um único arquivo plano.
Impact:      Impossibilidade de testar unidades isoladas, alto acoplamento entre domínios,
             dificulta manutenção e extensão. Qualquer alteração em um domínio pode quebrar outro.
Recommendation: Aplicar Playbook #1: God Class → MVC Split. Separar em módulos por domínio:
             models/produto.py, models/usuario.py, models/pedido.py; controllers/produto_controller.py,
             controllers/usuario_controller.py, controllers/pedido_controller.py.

[CRITICAL] Hardcoded Credentials
File:        app.py:7 | database.py:76-83 | controllers.py:289
Description: (1) app.py linha 7: SECRET_KEY Flask hardcoded como "minha-chave-super-secreta-123".
             (2) database.py linhas 76-83: seed de banco insere credenciais de usuários em texto
             puro diretamente no código — admin123, 123456, senha123.
             (3) controllers.py linha 289: endpoint /health expõe a secret_key via resposta JSON
             para qualquer cliente que acesse a rota.
Impact:      Exposição da SECRET_KEY em repositório compromete toda a segurança de sessões Flask.
             Credenciais de seed hardcoded são extraídas trivialmente do código-fonte ou do repositório.
             A exposição via /health torna o segredo público para qualquer consumidor da API.
Recommendation: Aplicar Playbook #2: Hardcoded Config → Settings Module. Mover SECRET_KEY e
             configurações de banco para variáveis de ambiente via python-dotenv. Remover a
             secret_key da resposta do health_check.

[CRITICAL] SQL Injection
File:        models.py:28 | models.py:47-50 | models.py:57-60 | models.py:68 |
             models.py:92 | models.py:109-110 | models.py:126-128 |
             models.py:140-165 | models.py:174 | models.py:188 | models.py:192 |
             models.py:220 | models.py:224 | models.py:280-281 | models.py:289-297
Description: Todas as queries SQL do projeto são construídas por concatenação de strings com
             dados externos. Exemplos críticos:
             - models.py:28: "SELECT * FROM produtos WHERE id = " + str(id)
             - models.py:109-110: "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
             - models.py:289-297: buscar_produtos monta query dinamicamente com termo, categoria,
               preco_min e preco_max vindos de query params sem sanitização
             - models.py:47-50: INSERT de produto com concatenação direta de strings
Impact:      Permite a qualquer usuário executar SQL arbitrário: extrair todos os dados,
             deletar tabelas, bypassar autenticação via clássico ' OR '1'='1. A função
             login_usuario é vulnerável a bypass total de autenticação.
Recommendation: Aplicar Playbook #3: SQL Injection → Parameterized Queries. Substituir toda
             concatenação por placeholders (?) com tuplas de parâmetros em cursor.execute().

[CRITICAL] Arbitrary SQL Execution
File:        app.py:59-78
Description: O endpoint POST /admin/query recebe o campo "sql" do corpo JSON da requisição
             e executa diretamente via cursor.execute(query), sem qualquer autenticação,
             autorização ou restrição de comandos. Aceita tanto SELECT quanto DDL/DML.
Impact:      Comprometimento total do banco de dados e potencialmente do servidor. Qualquer
             pessoa com acesso à rede pode executar DROP TABLE, DELETE sem WHERE, INSERT de
             dados, ou extrair toda a base. É equivalente a um shell SQL público.
Recommendation: REMOVER o endpoint imediatamente. Se necessário para administração, implementar
             apenas via CLI local com autenticação forte e nunca expor via HTTP.

[CRITICAL] Plaintext / Weak Password Storage
File:        database.py:75-83 | models.py:122-131 | models.py:105-120
Description: (1) database.py linhas 75-83: senhas inseridas no seed em texto puro ("admin123",
             "123456", "senha123") diretamente na coluna senha do banco SQLite.
             (2) models.py:122-131: função criar_usuario() insere a senha recebida sem nenhum
             processo de hashing — senha armazenada em texto claro.
             (3) models.py:105-120: login_usuario() compara senha via SQL direto (WHERE senha = '...'),
             sem hash. Não há uso de bcrypt, werkzeug.security ou argon2 em nenhum ponto.
Impact:      Em caso de vazamento do arquivo loja.db (que é um arquivo local sem senha),
             todas as senhas de todos os usuários ficam expostas em texto puro imediatamente.
             Impacto de credential stuffing em outros serviços dos usuários.
Recommendation: Aplicar Playbook #6: Plaintext/Weak Password → Bcrypt. Usar
             werkzeug.security.generate_password_hash() ao criar usuário e
             check_password_hash() ao fazer login.

[CRITICAL] Fake / Missing Authentication
File:        app.py:47-57 | app.py:59-78 | controllers.py:167-186
Description: (1) O endpoint POST /admin/reset-db deleta todos os dados das 4 tabelas sem
             qualquer verificação de autenticação ou autorização.
             (2) O endpoint POST /admin/query executa SQL arbitrário sem autenticação.
             (3) O endpoint POST /login (controllers.py:167-186) autentica o usuário mas
             retorna apenas os dados do usuário — não gera nenhum token (JWT, session cookie
             ou similar). Portanto não há mecanismo de autenticação funcional na API.
Impact:      Qualquer requisição HTTP para /admin/reset-db apaga toda a base. O sistema de
             login é inútil pois não emite credencial reutilizável — endpoints subsequentes
             não verificam autenticação.
Recommendation: Implementar autenticação JWT com PyJWT ou Flask-JWT-Extended. Proteger todos
             os endpoints sensíveis com decorator de verificação de token. Remover ou proteger
             fortemente os endpoints /admin/*.

--- HIGH ---

[HIGH] No Authentication on Sensitive Routes
File:        app.py:18-19 | app.py:28-29 | app.py:47 | app.py:59
Description: As seguintes rotas sensíveis não possuem nenhum middleware ou decorator de
             autenticação:
             - GET /usuarios (app.py:18): retorna todos os usuários incluindo senhas em texto puro
             - GET /relatorios/vendas (app.py:28-29): dados financeiros da loja
             - POST /admin/reset-db (app.py:47): destrói toda a base
             - POST /admin/query (app.py:59): SQL arbitrário
             Além disso, controllers.py:128-134 (listar_usuarios) retorna o campo "senha"
             em texto puro no JSON de resposta.
Impact:      Qualquer pessoa pode acessar dados de todos os usuários (incluindo senhas),
             relatórios financeiros e executar operações destrutivas sem se autenticar.
Recommendation: Implementar middleware de autenticação e aplicar em todas as rotas sensíveis.
             Remover o campo senha das respostas JSON de usuários em todas as funções de model.

[HIGH] Business Logic in Controller / Route Handler
File:        controllers.py:24-62 | controllers.py:64-96 | controllers.py:188-220 |
             models.py:133-169
Description: (1) controllers.py:24-62 (criar_produto): 38 linhas com validações de domínio
             (lista de categorias válidas, limites de nome, preço e estoque) misturadas no handler.
             (2) controllers.py:64-96 (atualizar_produto): mesma validação duplicada com 32 linhas.
             (3) controllers.py:188-220 (criar_pedido): simula envio de email, SMS e push
             notification dentro do controller via print() — responsabilidade de notificação
             acoplada ao handler HTTP.
             (4) models.py:133-169 (criar_pedido): lógica de negócio complexa (verificação de
             estoque, cálculo de total, atualização de estoque) implementada na camada de modelo.
Impact:      Violação do Single Responsibility Principle. Impossibilidade de reutilizar a
             lógica de validação. Dificuldade de testar regras de negócio isoladas.
             Lógica de notificação acoplada ao controller impede substituição por serviço real.
Recommendation: Aplicar Playbook #5: Heavy Route Handler → Controller. Extrair validações para
             uma camada de serviço (services/produto_service.py). Extrair notificações para
             services/notification_service.py.

--- MEDIUM ---

[MEDIUM] N+1 Query Problem
File:        models.py:171-201 | models.py:203-233
Description: (1) models.py:171-201 (get_pedidos_usuario): para cada pedido retornado, executa
             uma query para buscar os itens (SELECT FROM itens_pedido WHERE pedido_id = ?)
             e para cada item executa outra query para buscar o nome do produto
             (SELECT nome FROM produtos WHERE id = ?). Para N pedidos com M itens cada,
             executa 1 + N + N*M queries.
             (2) models.py:203-233 (get_todos_pedidos): mesmo padrão com escopo ainda maior
             (todos os pedidos do sistema).
Impact:      Degradação exponencial de performance com crescimento de dados. Com 100 pedidos
             de 5 itens cada, gera 601 queries ao invés de 3. Em produção causa timeout e
             degradação do serviço.
Recommendation: Aplicar Playbook #7: N+1 Query → JOIN. Usar JOIN entre pedidos, itens_pedido
             e produtos para trazer todos os dados em uma única query.

[MEDIUM] Code Duplication
File:        models.py:171-201 vs models.py:203-233 |
             controllers.py:24-62 vs controllers.py:64-96 |
             models.py:4-22 vs models.py:24-41 vs models.py:89-103
Description: (1) get_pedidos_usuario e get_todos_pedidos (models.py) são quase idênticos —
             mesma lógica de serialização de pedido com itens e produto_nome duplicada.
             (2) criar_produto e atualizar_produto (controllers.py) duplicam toda a validação
             de nome, preco, estoque e categoria (linhas 30-55 vs linhas 74-91).
             (3) Serialização de produto para dict duplicada em get_todos_produtos,
             get_produto_por_id e buscar_produtos (models.py:12-21, 31-40, 303-313).
Impact:      Inconsistências quando a lógica precisa ser atualizada — uma cópia é atualizada
             e a outra não. Manutenção custosa e propensa a erros.
Recommendation: Aplicar Playbook #8: Code Duplication → Helper/Service. Extrair serialização
             de produto para função _serialize_produto(). Extrair lógica de pedido com itens
             para _serialize_pedido(). Extrair validação de produto para _validate_produto_data().

[MEDIUM] Missing Input Validation
File:        controllers.py:111-126 | controllers.py:239-240 | models.py:72-87
Description: (1) controllers.py:111-126 (buscar_produtos): converte preco_min e preco_max de
             string para float sem try/except — "abc" como preco_min lança ValueError não tratado.
             (2) controllers.py:239-240 (atualizar_status_pedido): acessa dados.get("status")
             sem verificar se dados (request.get_json()) é None primeiro.
             (3) models.py:72-87 (get_todos_usuarios): retorna o campo "senha" em texto puro
             na lista de todos os usuários — dado sensível exposto sem necessidade.
Impact:      Erros 500 inesperados para input malformado em vez de 400 com mensagem clara.
             Exposição desnecessária de senhas em texto puro para qualquer consumidor do endpoint.
Recommendation: Adicionar try/except para conversões de tipo. Validar request.get_json() antes
             de acessar campos. Remover campo senha das respostas de listagem de usuários.

[MEDIUM] Deprecated / Insecure APIs
File:        models.py:1-315 | database.py:1-87
Description: Uso de sqlite3 raw (sem ORM) em todas as 15+ operações de banco de dados do
             projeto. O acesso direto via sqlite3 sem camada de abstração torna SQL Injection
             trivial (como evidenciado pelos 15+ pontos de injeção encontrados). Além disso,
             a comparação de senha é feita via SQL (WHERE senha = '...') ao invés de comparação
             de hash criptográfico seguro.
Impact:      Vulnerabilidades de segurança conhecidas e dificuldade de migrar para outro banco.
             A ausência de ORM ou query builder seguro torna o código inerentemente propenso
             a SQL Injection.
Recommendation: Migrar para SQLAlchemy ou usar parameterized queries consistentemente.
             Adotar werkzeug.security para hashing e comparação de senhas.

--- LOW ---

[LOW] Debug / Print Logging
File:        app.py:8 | app.py:88 | controllers.py:8,11,57,106,161,179,182,208-210,219,248-250
Description: (1) app.py:8: DEBUG=True hardcoded na configuração — expõe debugger Werkzeug.
             (2) app.py:88: app.run(host="0.0.0.0", debug=True) — expõe o debugger interativo
             do Werkzeug em todas as interfaces de rede, permitindo execução de código arbitrário
             via /console do debugger.
             (3) 11 chamadas print() espalhadas em controllers.py usadas como mecanismo de
             logging — incluindo print() com emails de usuário (linha 161, 179, 182) e
             simulações de notificação (linhas 208-210, 248-250).
Impact:      O Werkzeug debugger ativo em 0.0.0.0 permite execução de código Python arbitrário
             por qualquer usuário na rede. Emails de usuários logados em stdout em produção
             violam LGPD/GDPR. Print statements não são capturáveis por sistemas de log centralizados.
Recommendation: Configurar DEBUG via variável de ambiente (DEBUG=os.environ.get('FLASK_DEBUG', 'False')).
             Substituir todos os print() por logging.getLogger(__name__) com níveis apropriados
             (logging.info, logging.error).

================================
REFACTORING PRIORITY
================================
1. [CRITICAL] Arbitrary SQL Execution    — app.py:59-78          → REMOVER endpoint /admin/query
2. [CRITICAL] SQL Injection              — models.py (15+ pontos) → Playbook #3
3. [CRITICAL] Plaintext Password Storage — models.py + database.py → Playbook #6
4. [CRITICAL] Fake/Missing Auth          — app.py + controllers.py → Implementar JWT
5. [CRITICAL] Hardcoded Credentials      — app.py:7 + database.py  → Playbook #2
6. [CRITICAL] God Class / God Method     — models.py + controllers  → Playbook #1
7. [HIGH]     No Auth on Sensitive Routes — app.py (múltiplas)    → Middleware de auth
8. [HIGH]     Business Logic in Handler  — controllers.py + models → Playbook #5

================================
Total: 13 findings
Refactoring required: YES
================================
```
