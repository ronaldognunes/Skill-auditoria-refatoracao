# Architecture Audit Report — ecommerce-api-legacy

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express 4.18.2
Files:   3 analyzed | ~181 lines of code

================================
SUMMARY
================================
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 1
Total:    11 findings

================================
FINDINGS
================================

--- CRITICAL ---

[CRITICAL] God Class / God Method
File:        src/AppManager.js:1-141
Description: A classe AppManager concentra 5 responsabilidades distintas: inicialização
             do banco (initDb), configuração de rotas (setupRoutes), lógica de negócio
             do checkout (validação de curso, criação de usuário, processamento de
             pagamento, criação de matrícula), lógica de relatório financeiro, e
             gerenciamento de auditoria — tudo em uma única classe de 141 linhas.
             O construtor cria a conexão com o banco, methods de rota contêm CREATE
             TABLE e INSERT diretamente junto com handlers HTTP.
Impact:      Impossibilidade de testar unidades isoladas; alto acoplamento entre
             camadas HTTP, lógica de negócio e acesso a dados; qualquer modificação
             em uma responsabilidade arrisca quebrar as demais.
Recommendation: Aplicar Playbook #1: God Class → MVC Split. Separar em:
             UserModel, CourseModel, EnrollmentModel (acesso a dados);
             CheckoutController, ReportController (lógica de negócio);
             checkoutRoutes, adminRoutes (roteamento HTTP).

[CRITICAL] Hardcoded Credentials
File:        src/utils.js:2-6
Description: Quatro credenciais embutidas diretamente no código-fonte:
             dbPass: "senha_super_secreta_prod_123" (senha do banco de produção),
             paymentGatewayKey: "pk_live_1234567890abcdef" (chave live do gateway),
             smtpUser: "no-reply@fullcycle.com.br" (conta de email).
             Adicionalmente, AppManager.js:18 insere seed com senha plaintext '123'.
Impact:      Credenciais visíveis em qualquer repositório git (público ou privado
             comprometido), em logs, em builds CI/CD. Comprometimento imediato de
             sistemas de produção se o repositório vazar.
Recommendation: Aplicar Playbook #2: Hardcoded Config → Settings Module.
             Mover para src/config/settings.js usando process.env. Criar .env
             para desenvolvimento e adicionar ao .gitignore.

[CRITICAL] Plaintext / Weak Password Storage
File:        src/utils.js:17-23, src/AppManager.js:68
Description: Função badCrypto() usa Base64 (codificação, não hash) em loop de
             10.000 iterações, truncando para 10 caracteres. Base64 é completamente
             reversível — não é criptografia. A senha resultante tem apenas 10 chars
             de espaço de possibilidades mínimo. Linha 68 usa "123456" como senha
             padrão se nenhuma for fornecida. Seed em AppManager.js:18 salva '123'
             como senha sem hash.
Impact:      Todas as senhas são recuperáveis trivialmente. Em caso de vazamento
             do banco, 100% das contas ficam comprometidas imediatamente.
Recommendation: Aplicar Playbook #6: Plaintext/Weak Password → Bcrypt.
             Substituir badCrypto() por bcrypt.hash() com SALT_ROUNDS=12.
             Remover senha padrão "123456". Rejeitar requisições sem senha.

[CRITICAL] Fake / Missing Authentication
File:        src/AppManager.js:80-129, src/AppManager.js:131-137
Description: Zero implementação de autenticação em toda a aplicação. O endpoint
             GET /api/admin/financial-report retorna dados financeiros completos
             (receita por curso, lista de alunos e valores pagos) sem qualquer
             verificação de identidade. O endpoint DELETE /api/users/:id permite
             deletar qualquer usuário sem autenticação. Não existe nenhum middleware
             de auth, JWT, session, ou qualquer mecanismo de controle de acesso.
Impact:      Qualquer pessoa na internet pode acessar todos os dados financeiros
             e deletar qualquer usuário. Violação grave de LGPD/GDPR.
Recommendation: Implementar JWT authentication middleware. Adicionar middleware
             de autenticação nas rotas sensíveis. Implementar RBAC para separar
             acesso de admin vs. usuário comum.

--- HIGH ---

[HIGH] No Authentication on Sensitive Routes
File:        src/AppManager.js:80, src/AppManager.js:131
Description: As rotas /api/admin/financial-report e DELETE /api/users/:id são
             explicitamente "admin" mas não possuem nenhum middleware de autenticação.
             Em Express, app.get('/api/admin/financial-report', handler) sem middleware
             intermediário significa acesso público irrestrito.
Impact:      Exposição de dados financeiros sensíveis (receita, alunos, valores
             pagos) a qualquer requisição anônima.
Recommendation: Adicionar middleware de autenticação antes dos handlers:
             app.get('/api/admin/financial-report', authMiddleware, adminMiddleware, handler)

[HIGH] Business Logic in Route Handler
File:        src/AppManager.js:28-78 (checkout, 50 linhas), src/AppManager.js:80-129
             (financial-report, 49 linhas)
Description: O handler do POST /api/checkout contém 50 linhas com: validação de
             curso, lookup/criação de usuário, processamento de pagamento, criação
             de matrícula, log de auditoria e caching — tudo dentro do callback
             da rota. O handler do financial-report contém toda a lógica de
             agregação de dados com loops e queries aninhadas.
Impact:      Impossibilidade de reusar lógica de checkout em outros contextos
             (ex: CLI, testes). Violação do Single Responsibility Principle.
             Handlers com 50+ linhas são impossíveis de testar unitariamente.
Recommendation: Aplicar Playbook #5: Heavy Route Handler → Controller.
             Extrair para CheckoutController.processCheckout() e
             ReportController.getFinancialReport().

[HIGH] Callback Hell (Node.js)
File:        src/AppManager.js:37-77
Description: O checkout possui 5 níveis de callbacks aninhados:
             db.get(course) → db.get(user) → processPaymentAndEnroll →
             db.run(enrollment) → db.run(payment) → db.run(audit_log).
             A pirâmide de indentação torna o fluxo de erro não-linear e
             dificulta rastreamento de exceções.
Impact:      Código ilegível e propenso a erros de tratamento de exceção. Race
             conditions silenciosas quando callbacks falham sem propagar o erro
             corretamente (linha 57: erro de audit_log é ignorado).
Recommendation: Aplicar Playbook #4: Callback Hell → Async/Await.
             Promisificar db.get/db.run/db.all e reescrever com async/await.

--- MEDIUM ---

[MEDIUM] N+1 Query Problem
File:        src/AppManager.js:89-126
Description: O financial-report executa queries dentro de loops aninhados:
             1 query (cursos) → N queries (matrículas por curso) → N×M queries
             (usuário + pagamento por matrícula). Para 2 cursos com 2 matrículas
             cada: 1 + 2 + (2×2×2) = 11 queries. Para 10 cursos com 100
             matrículas: 1 + 10 + 2000 = 2011 queries.
Impact:      Degradação de performance exponencial (O(n×m)) com crescimento
             de dados. Timeout em produção com volume real.
Recommendation: Aplicar Playbook #7: N+1 Query → JOIN. Substituir os loops
             por uma query com JOINs:
             SELECT c.title, u.name, p.amount, p.status
             FROM courses c
             LEFT JOIN enrollments e ON e.course_id = c.id
             LEFT JOIN users u ON u.id = e.user_id
             LEFT JOIN payments p ON p.enrollment_id = e.id

[MEDIUM] Missing Input Validation
File:        src/AppManager.js:35, src/AppManager.js:132
Description: Linha 35 verifica apenas presença de campos (truthy check), sem
             validação de formato: email não é validado como email, course_id
             não é verificado como inteiro, card number não tem validação de
             formato real. Linha 132: req.params.id é string usada diretamente
             como parâmetro sem conversão ou validação numérica.
Impact:      Erros inesperados em produção com dados malformados. Possibilidade
             de inserir emails inválidos no banco.
Recommendation: Adicionar validação de schema (joi ou zod) para todos os
             endpoints. Converter req.params.id para parseInt() com verificação.

[MEDIUM] Deprecated / Insecure APIs (Roll Your Own Crypto)
File:        src/utils.js:17-23
Description: Implementação de criptografia customizada (badCrypto) que usa
             Buffer.from().toString('base64') — uma codificação reversível —
             ao invés de algoritmo de hashing real. É o anti-pattern clássico
             "roll your own crypto". O nome badCrypto admite explicitamente o
             problema mas o código permanece em uso (AppManager.js:68).
Impact:      Vulnerabilidade de segurança crítica mascarada como código legado.
             Base64 pode ser decodificado com uma linha de código.
Recommendation: Remover badCrypto completamente. Usar bcrypt (Playbook #6).

--- LOW ---

[LOW] Debug / Print Logging com Dados Sensíveis
File:        src/AppManager.js:45, src/utils.js:13
Description: Linha 45: console.log loga número completo do cartão de crédito
             (variável cc) e a chave live do gateway de pagamento juntos:
             "Processando cartão ${cc} na chave ${config.paymentGatewayKey}".
             Linha 13: console.log registra chaves de cache para cada operação.
Impact:      Dados de cartão de crédito em logs violam PCI-DSS. Chave live do
             gateway exposta em logs de aplicação. Em sistemas com log
             centralizado (ELK, Datadog), dados ficam armazenados indefinidamente.
Recommendation: Remover console.log com dados sensíveis. Nunca logar dados de
             cartão. Usar structured logging (winston/pino) com mascaramento
             de dados sensíveis.

================================
REFACTORING PRIORITY
================================
1. [CRITICAL] Fake/Missing Authentication    — AppManager.js  → JWT middleware
2. [CRITICAL] Hardcoded Credentials          — utils.js       → Playbook #2
3. [CRITICAL] Weak Password Storage          — utils.js       → Playbook #6
4. [CRITICAL] God Class / God Method         — AppManager.js  → Playbook #1
5. [HIGH]     Callback Hell                  — AppManager.js  → Playbook #4
6. [HIGH]     Business Logic in Handler      — AppManager.js  → Playbook #5
7. [HIGH]     No Auth on Sensitive Routes    — AppManager.js  → JWT middleware

================================
Total: 11 findings
Refactoring required: YES
================================
```
