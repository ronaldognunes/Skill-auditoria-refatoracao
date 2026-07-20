# Audit Report Template

Use este template para formatar o relatório de auditoria gerado na Fase 2.

Substitua todos os placeholders `<...>` pelos valores reais encontrados na análise.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem> + <framework>
Files:   <n> analyzed | ~<linhas> lines of code

================================
SUMMARY
================================
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Total:    <n> findings

================================
FINDINGS
================================

--- CRITICAL ---

[CRITICAL] <Nome do Anti-Pattern>
File:        <arquivo>:<linha_início>-<linha_fim>
Description: <o que exatamente foi encontrado no código>
Impact:      <impacto arquitetural e/ou de segurança>
Recommendation: <como corrigir — referência ao playbook se aplicável>

[CRITICAL] <Nome do Anti-Pattern>
File:        <arquivo>:<linha_início>-<linha_fim>
Description: <o que exatamente foi encontrado no código>
Impact:      <impacto arquitetural e/ou de segurança>
Recommendation: <como corrigir>

--- HIGH ---

[HIGH] <Nome do Anti-Pattern>
File:        <arquivo>:<linha_início>-<linha_fim>
Description: <o que exatamente foi encontrado no código>
Impact:      <impacto arquitetural e/ou de segurança>
Recommendation: <como corrigir>

--- MEDIUM ---

[MEDIUM] <Nome do Anti-Pattern>
File:        <arquivo>:<linha_início>-<linha_fim>
Description: <o que exatamente foi encontrado no código>
Impact:      <impacto de performance ou manutenibilidade>
Recommendation: <como corrigir>

--- LOW ---

[LOW] <Nome do Anti-Pattern>
File:        <arquivo>:<linha_início>-<linha_fim>
Description: <o que exatamente foi encontrado no código>
Impact:      <impacto menor>
Recommendation: <como corrigir>

================================
REFACTORING PRIORITY
================================
1. [CRITICAL] <Anti-Pattern> — <arquivo> → Playbook #<n>
2. [CRITICAL] <Anti-Pattern> — <arquivo> → Playbook #<n>
3. [HIGH]     <Anti-Pattern> — <arquivo> → Playbook #<n>
...

================================
Total: <n> findings
Refactoring required: YES / NO
================================
```

---

## Notas de Preenchimento

- **File:** inclua sempre o caminho relativo à raiz do projeto e as linhas exatas (ex: `models.py:28-35`)
- **Description:** seja específico — cite o trecho de código ou o nome da variável/função problemática
- **Impact:** descreva consequências reais (ex: "permite execução de SQL arbitrário", "degrada performance em O(n²)")
- **Recommendation:** referencie o playbook quando aplicável (ex: "Aplicar Playbook #3: SQL Injection → Parameterized Queries")
- **Refactoring Priority:** liste apenas os findings CRITICAL e HIGH, ordenados por risco

## Localização do Relatório

Salve o relatório em:
```
<raiz-do-repositório>/reports/audit-<project-name>.md
```

Exemplos:
- `reports/audit-code-smells-project.md`
- `reports/audit-ecommerce-api-legacy.md`
- `reports/audit-task-manager-api.md`
