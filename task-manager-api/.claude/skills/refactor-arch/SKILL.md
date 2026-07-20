# Skill: /refactor-arch

Você é um agente especializado em auditoria arquitetural e refatoração de código legado para o padrão MVC. Ao ser invocado, execute as 3 fases abaixo em sequência, usando os arquivos de suporte desta pasta.

---

## FASE 1 — Análise do Projeto

Inspecione todos os arquivos de código fonte do projeto atual e produza um sumário estruturado:

1. Use `project-analysis.md` para identificar:
   - Linguagem principal (Python, JavaScript, TypeScript)
   - Framework (Flask, Express, Django, etc.)
   - Banco de dados (SQLite, PostgreSQL, MongoDB, etc.)
   - Arquitetura atual (monolítico, MVC parcial, sem camadas)
   - Domínio da aplicação (e-commerce, LMS, task manager, etc.)

2. Conte arquivos por extensão e estime linhas de código

3. Imprima o sumário no seguinte formato:

```
================================
PROJECT ANALYSIS
================================
Project:      <nome do diretório>
Language:     <linguagem>
Framework:    <framework> <versão se disponível>
Database:     <banco de dados>
Architecture: <arquitetura atual>
Domain:       <domínio>

Files:        <n> source files
Code:         ~<linhas> lines of code
Entry Point:  <arquivo principal>
================================
```

---

## FASE 2 — Auditoria de Anti-Patterns

1. Abra e leia `antipatterns-catalog.md`
2. Para cada anti-pattern do catálogo, verifique se o sinal de detecção está presente no código
3. Para cada finding encontrado, registre:
   - Severidade (CRITICAL, HIGH, MEDIUM, LOW)
   - Nome do anti-pattern
   - Arquivo e linha(s) exatas
   - Descrição do que foi encontrado
   - Impacto arquitetural e/ou de segurança
   - Recomendação de correção

4. Use `audit-report-template.md` para formatar o relatório
5. Exiba os findings ordenados por severidade: CRITICAL → HIGH → MEDIUM → LOW
6. Salve o relatório em `../reports/audit-<project-name>.md` (relativo à raiz do repositório)

**IMPORTANTE: Após exibir o relatório completo, PAUSAR e perguntar:**

```
Deseja prosseguir com a refatoração? [y/n]
```

Aguarde a resposta antes de continuar. Se a resposta for `n`, encerre aqui.

---

## FASE 3 — Refatoração para MVC (somente após confirmação)

1. Abra `architecture-guidelines.md` para a estrutura MVC alvo da linguagem detectada
2. Abra `refactoring-playbook.md` para os padrões de transformação aplicáveis
3. Para cada finding CRITICAL e HIGH, aplique o padrão de refatoração correspondente:

   | Anti-Pattern | Playbook |
   |---|---|
   | God Class/Method | Padrão 1: God Class → MVC Split |
   | Hardcoded Credentials | Padrão 2: Hardcoded Config → Settings Module |
   | SQL Injection | Padrão 3: SQL Injection → Parameterized Queries |
   | Plaintext/Weak Passwords | Padrão 6: Plaintext/Weak Password → Bcrypt |
   | Callback Hell | Padrão 4: Callback Hell → Async/Await |
   | Heavy Route Handler | Padrão 5: Heavy Route Handler → Controller |
   | N+1 Query | Padrão 7: N+1 Query → JOIN |
   | Code Duplication | Padrão 8: Code Duplication → Helper/Service |
   | No Error Handling | Padrão 9: No Error Handling → Centralized Handler |

4. **Preservar todos os endpoints originais e seus contratos de request/response**
5. Criar a estrutura de diretórios MVC conforme `architecture-guidelines.md`
6. Após refatorar, validar:
   - `python app.py` ou `node src/app.js` sobe sem erros
   - Endpoints principais respondem corretamente

7. Imprimir sumário final:

```
================================
REFACTORING COMPLETE
================================
Structure:
<árvore de diretórios final>

Validations:
[ ] Application starts without errors
[ ] All original endpoints preserved
[ ] No hardcoded credentials
[ ] Parameterized queries in use
[ ] Password hashing with bcrypt/werkzeug
[ ] MVC layers properly separated

Anti-patterns resolved: <n>/<total>
================================
```
