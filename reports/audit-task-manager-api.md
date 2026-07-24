================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   10 analyzed | ~1060 lines of code

================================
SUMMARY
================================
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 12
Total:    20 findings

================================
FINDINGS
================================

--- CRITICAL ---

[CRITICAL] Hardcoded Credentials
File:        app.py:13 | services/notification_service.py:7-10
Description: SECRET_KEY do Flask hardcoded como 'super-secret-key-123' em app.py.
             Credenciais de email hardcoded em NotificationService.__init__():
             self.email_user = 'taskmanager@gmail.com' e self.email_password = 'senha123'.
Impact:      Exposição de segredos em repositórios públicos. Qualquer pessoa com acesso
             ao código pode comprometer sessões Flask (forjando cookies de sessão) e
             as credenciais do servidor de email.
Recommendation: Aplicar Playbook #2: Hardcoded Config → Settings Module.
             Criar src/config/settings.py com os.getenv() para todas as configurações.
             Adicionar .env ao .gitignore e fornecer .env.example.

[CRITICAL] Plaintext / Weak Password Storage
File:        models/user.py:29,32
Description: Senhas armazenadas com MD5 sem salt: hashlib.md5(pwd.encode()).hexdigest()
             em set_password() e check_password(). MD5 é reversível com rainbow tables.
             Adicionalmente, to_dict() (user.py:16-25) expõe o hash da senha no campo
             'password' em todas as respostas da API (incluindo GET /users/<id> e /login).
Impact:      Em caso de vazamento do banco, todas as senhas podem ser quebradas em minutos
             com ferramentas como hashcat. A exposição do hash na API amplia o vetor de ataque.
Recommendation: Aplicar Playbook #6: Plaintext/Weak Password → Bcrypt.
             Substituir hashlib.md5 por werkzeug.security.generate_password_hash /
             check_password_hash. Remover 'password' do campo retornado em to_dict().

[CRITICAL] Fake / Missing Authentication Token
File:        routes/user_routes.py:210
Description: O endpoint POST /login retorna 'token': 'fake-jwt-token-' + str(user.id).
             O token é construído apenas com o ID do usuário, sem assinatura criptográfica,
             expiração ou qualquer verificação. Qualquer usuário pode forjar o token de outro
             simplesmente conhecendo o ID (ex: 'fake-jwt-token-1' para o admin).
Impact:      Acesso não autorizado a qualquer conta. Bypass completo de autenticação.
             Escalada de privilégio trivial para contas admin.
Recommendation: Implementar JWT real com flask-jwt-extended ou PyJWT, usando SECRET_KEY
             via variável de ambiente, tempo de expiração e verificação de assinatura em
             todas as rotas protegidas.

--- HIGH ---

[HIGH] No Authentication on Sensitive Routes
File:        routes/user_routes.py:10,27,42,92,134,153,185 |
             routes/task_routes.py:11,65,85,156,225,240,273 |
             routes/report_routes.py:12,103,157,167,190,211
Description: Nenhuma rota possui middleware ou decorator de autenticação. Operações
             destrutivas (DELETE /users/<id>, DELETE /tasks/<id>) e relatórios sensíveis
             (GET /reports/summary, GET /reports/user/<id>) estão publicamente acessíveis
             sem qualquer verificação de identidade.
Impact:      Qualquer requisição anônima pode deletar usuários e tarefas, acessar dados
             de todos os usuários, e consultar relatórios de produtividade da equipe.
Recommendation: Implementar middleware de autenticação (decorator @login_required ou
             verificação de JWT) e aplicar em todas as rotas. Verificar também que apenas
             admins possam acessar rotas /users (CRUD completo) e /reports.

[HIGH] Business Logic in Route Handler
File:        routes/task_routes.py:11-63 (get_tasks, 52 linhas),
             routes/task_routes.py:85-154 (create_task, 70 linhas),
             routes/task_routes.py:156-223 (update_task, 67 linhas),
             routes/report_routes.py:12-101 (summary_report, 89 linhas),
             routes/user_routes.py:42-90 (create_user, 48 linhas)
Description: Handlers de rota contêm validação de domínio, cálculos de negócio e
             acesso direto ao banco via ORM — tudo misturado. Ex: get_tasks() executa
             lógica de overdue, lookup de User e Category inline; summary_report() calcula
             métricas de produtividade por usuário diretamente no handler.
             Camada de controllers/ é completamente ausente.
Impact:      Impossibilidade de testar lógica de negócio em isolamento. Violação do SRP.
             Lógica de validação (título, status, prioridade) duplicada entre create e update.
Recommendation: Aplicar Playbook #5: Heavy Route Handler → Controller e Playbook #1:
             God Class → MVC Split. Criar src/controllers/ com TaskController,
             UserController e ReportController. Handlers de rota devem ter ≤10 linhas.

--- MEDIUM ---

[MEDIUM] N+1 Query Problem
File:        routes/task_routes.py:41-57 | routes/report_routes.py:53-68
Description: Em get_tasks(): para cada task retornada, são feitas 2 queries adicionais:
             User.query.get(t.user_id) e Category.query.get(t.category_id).
             Para N tasks, resultado = 1 + 2N queries.
             Em summary_report(): para cada usuário, Task.query.filter_by(user_id=u.id).all()
             é chamado separadamente. Para M usuários, resultado = 1 + M queries.
Impact:      Degradação exponencial de performance com crescimento de dados.
             Com 100 tasks, get_tasks() executa até 201 queries desnecessárias.
Recommendation: Aplicar Playbook #7: N+1 Query → JOIN.
             Usar SQLAlchemy joinedload/subqueryload ou reescrever com JOIN explícito.
             Ex: Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

[MEDIUM] Code Duplication
File:        routes/task_routes.py:30-39, 71-80, 284-287 |
             routes/user_routes.py:171-180 |
             routes/report_routes.py:34-37, 132-135 |
             models/task.py:50-60
Description: O bloco de cálculo de overdue (verificar due_date < utcnow() e status
             != 'done'/'cancelled') está duplicado em 6 lugares distintos, apesar de
             existir o método task.is_overdue() em models/task.py que nunca é usado.
             Validação de email com o mesmo regex duplicada em user_routes.py:61 e :106,
             sendo que validate_email() já existe em utils/helpers.py mas não é utilizada.
Impact:      Inconsistências ao atualizar a lógica (ex: adicionar novo status 'archived').
             Violação do princípio DRY. Manutenção em 6+ lugares para uma única regra.
Recommendation: Aplicar Playbook #8: Code Duplication → Helper/Service.
             Usar task.is_overdue() existente em todos os handlers.
             Usar validate_email() de utils/helpers.py nos route handlers.

[MEDIUM] Missing Input Validation
File:        routes/report_routes.py:197 | routes/task_routes.py:113,261
Description: Em update_category(): data = request.get_json() pode retornar None quando
             Content-Type não é application/json, mas 'if name in data' (linha 197) é
             chamado sem verificar se data é None — causará TypeError em produção.
             Em create_task(): priority = data.get('priority', 3) recebe valor sem
             validação de tipo antes de if priority < 1 (linha 113) — se enviado como
             string '3', a comparação falhará com TypeError.
             Em search_tasks(): int(priority) na linha 261 não trata ValueError se
             priority não for numérico.
Impact:      Erros 500 inesperados com inputs malformados. Mensagens de erro técnicas
             expostas ao cliente. Potencial para comportamento indefinido.
Recommendation: Validar request.get_json() antes de usar. Converter e validar tipos
             explicitamente. Considerar marshmallow (já na requirements.txt) para
             validação de schema centralizada.

--- LOW ---

[LOW] Debug / Print Logging
File:        app.py:34 | routes/user_routes.py:83,89,147 |
             routes/task_routes.py:149,153,219,234 |
             services/notification_service.py:21,24
Description: app.run(debug=True, host='0.0.0.0') expõe o Werkzeug debugger interativo
             em todas as interfaces de rede — permite execução de código arbitrário no
             servidor a qualquer visitante que provoque um erro.
             9 chamadas print() usadas como mecanismo de logging em produção,
             incluindo print(f"ERRO: {str(e)}") que expõe stack traces.
Impact:      Com debug=True e host='0.0.0.0', um atacante pode executar código Python
             arbitrário no servidor via Werkzeug debugger console. Print não é adequado
             para produção (sem levels, sem timestamps estruturados, sem rotação de logs).
Recommendation: Controlar debug via variável de ambiente: DEBUG=os.getenv('DEBUG','false')=='true'.
             Substituir print() pelo módulo logging com níveis apropriados (INFO, ERROR).
             Nunca fazer host='0.0.0.0' com debug=True em produção.

[LOW] Magic Numbers — Limites de Validação em task_routes.py
File:        routes/task_routes.py:72,74,85
Description: Validações de título usam literais < 3 e > 200 e prioridade usa < 1 e > 5
             diretamente nas comparações. Os números não possuem nomes simbólicos que
             comuniquem o significado de negócio de cada limite.
Impact:      Alterar limites exige busca manual por literais em múltiplos pontos.
             Código não comunica por que 200 é o máximo de caracteres ou por que 5
             é a prioridade máxima.
Recommendation: Extrair em utils/helpers.py: MIN_TITLE_LENGTH = 3, MAX_TITLE_LENGTH = 200,
             MIN_PRIORITY = 1, MAX_PRIORITY = 5 e importar nos route handlers.

[LOW] Magic Numbers — Limites de Validação em user_routes.py
File:        routes/user_routes.py:63,70
Description: Validação de senha usa literal < 4 e validação de role compara contra a
             lista inline ['user', 'admin', 'manager'] sem constante nomeada.
Impact:      Listas de valores válidos duplicadas em create e update de usuário.
             Alterar comprimento mínimo de senha ou adicionar novo role exige busca global.
Recommendation: Extrair MIN_PASSWORD_LENGTH = 4 e VALID_ROLES = ['user', 'admin', 'manager']
             em utils/helpers.py.

[LOW] Magic Numbers — Thresholds em report_routes.py
File:        routes/report_routes.py:24-28
Description: O summary_report usa literais numéricos para calcular médias e percentuais
             de conclusão de tarefas sem constantes nomeadas para os thresholds utilizados.
Impact:      Thresholds de relatório sem nome simbólico dificultam ajuste de métricas
             de produtividade sem alterar lógica de apresentação.
Recommendation: Extrair constantes nomeadas para thresholds de produtividade.

[LOW] Nomenclatura Ruim — Variáveis p1 a p5 em report_routes.py
File:        routes/report_routes.py:24-28
Description: Contadores de prioridade são nomeados p1, p2, p3, p4, p5 em vez de nomes
             que comunicam a prioridade que cada variável representa.
Impact:      p1 pode significar "prioridade 1 (crítica)" ou "primeiro parâmetro". O
             leitor precisa rastrear o código para descobrir o significado.
Recommendation: Renomear para priority_critical, priority_high, priority_medium,
             priority_low, priority_minimal.

[LOW] Nomenclatura Ruim — Variável 'd' em models/category.py
File:        models/category.py:14
Description: A função to_dict() usa d = {} como nome do dicionário de retorno, uma
             abreviação de uma letra sem semântica fora de contexto de iteração.
Impact:      Nome genérico reduz legibilidade; convenção de uma letra deve ser reservada
             para índices de loop (i, j, k).
Recommendation: Renomear para result = {} ou category_dict = {}.

[LOW] Nomenclatura Ruim — Parâmetro 'p' em models/task.py
File:        models/task.py:45
Description: O método validate_priority(self, p) usa p como nome do parâmetro de
             prioridade, abreviação que não comunica o tipo ou domínio do valor recebido.
Impact:      Ao ler a assinatura do método, p é ambíguo (poderia ser page, product,
             ou qualquer outra coisa começando com p).
Recommendation: Renomear o parâmetro para value ou priority_value.

[LOW] Código Morto — Imports Não Utilizados em task_routes.py
File:        routes/task_routes.py:7
Description: As linhas import json, import os, import sys e import time estão presentes
             em task_routes.py mas nenhum desses módulos é referenciado no corpo do arquivo.
Impact:      Imports desnecessários aumentam tempo de carregamento e confundem sobre
             dependências reais do módulo.
Recommendation: Remover as 4 linhas de import não utilizadas.

[LOW] Código Morto — Imports Não Utilizados em user_routes.py
File:        routes/user_routes.py:6
Description: import hashlib e import json estão presentes mas não são usados em
             nenhuma função de user_routes.py após a migração para werkzeug.security.
Impact:      hashlib importado sugere falsamente que ainda há hashing manual no arquivo.
Recommendation: Remover import hashlib e import json de user_routes.py.

[LOW] Código Morto — Funções Importadas Sem Uso em report_routes.py
File:        routes/report_routes.py:7
Description: from utils.helpers import format_date, calculate_percentage importa duas
             funções que não são chamadas em nenhum ponto de report_routes.py.
Impact:      Import morto sugere que o arquivo usa helpers de formatação quando não usa.
             Confunde ao auditar dependências do módulo de relatórios.
Recommendation: Remover o import de format_date e calculate_percentage de report_routes.py.

[LOW] Código Morto — Imports Não Utilizados em utils/helpers.py
File:        utils/helpers.py:2-7
Description: O arquivo helpers.py importa os, json, sys, math e hashlib. Nenhum desses
             módulos é referenciado nas funções definidas no arquivo.
Impact:      5 imports desnecessários poluem o módulo utilitário. hashlib sugere
             falsamente que há operações criptográficas no arquivo.
Recommendation: Remover todos os imports não utilizados de utils/helpers.py.

[LOW] Código Morto — Funções Nunca Chamadas em utils/helpers.py
File:        utils/helpers.py:27-83
Description: As funções generate_id(), is_valid_color() e process_task_data() estão
             definidas em utils/helpers.py mas não são importadas ou chamadas em nenhum
             ponto do projeto (verificado em todos os arquivos de routes e models).
Impact:      Código morto que polui o módulo, aumenta esforço de leitura e pode
             mascarar código legado que deveria ter sido removido.
Recommendation: Remover as 3 funções. Se process_task_data contiver lógica relevante,
             migrar para a camada de serviço apropriada antes de remover.

================================
REFACTORING PRIORITY
================================
1. [CRITICAL] Fake Authentication Token     — routes/user_routes.py:210  → Implementar JWT real
2. [CRITICAL] Hardcoded Credentials         — app.py:13, notification_service.py:9-10 → Playbook #2
3. [CRITICAL] Weak Password Storage (MD5)   — models/user.py:29,32       → Playbook #6
4. [HIGH]     No Auth on Sensitive Routes   — todas as routes             → Middleware JWT
5. [HIGH]     Business Logic in Route       — task_routes.py, report_routes.py, user_routes.py → Playbook #1 + #5

================================
Total: 20 findings
Refactoring required: YES
================================
