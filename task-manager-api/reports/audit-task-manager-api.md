================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   ~18 analyzed | ~600 lines of code

================================
SUMMARY (LOW findings only — rodada de auditoria incremental)
================================
CRITICAL: - | HIGH: - | MEDIUM: - | LOW: 11
Total:    11 LOW findings

================================
FINDINGS
================================

--- LOW ---

[LOW] #15 Magic Numbers
File:        routes/task_routes.py:72,74,85
Description: Literais 3 e 200 para validação de comprimento de título (criar e atualizar task) e literais 1 e 5 para validação de prioridade. As constantes MIN_TITLE_LENGTH e MAX_TITLE_LENGTH existem em utils/helpers.py mas não são importadas.
Impact:      Valores duplicados entre helpers.py e routes; qualquer alteração de limite deve ser feita manualmente em múltiplos lugares.
Recommendation: Importar MIN_TITLE_LENGTH, MAX_TITLE_LENGTH, MIN_PRIORITY, MAX_PRIORITY de utils/helpers.py e usar nas validações.

[LOW] #15 Magic Numbers
File:        routes/user_routes.py:63,70
Description: Literal 4 para comprimento mínimo de senha e lista literal ['user', 'admin', 'manager'] para validação de roles. Constantes MIN_PASSWORD_LENGTH e VALID_ROLES existem em helpers.py mas não são importadas.
Impact:      Regras de negócio duplicadas; alterar roles válidas ou tamanho mínimo de senha exige busca manual.
Recommendation: Importar MIN_PASSWORD_LENGTH e VALID_ROLES de utils/helpers.py.

[LOW] #15 Magic Numbers
File:        routes/report_routes.py:24-28
Description: Priority values 1, 2, 3, 4, 5 usados diretamente em queries filter_by(priority=N) sem constantes descritivas. Os números de prioridade não comunicam seus significados (critical, high, medium, low, minimal).
Impact:      Código difícil de entender; o leitor precisa saber a semântica dos números de prioridade de cabeça.
Recommendation: Adicionar constantes MIN_PRIORITY e MAX_PRIORITY no helpers.py; usar variáveis com nomes semânticos para cada nível.

[LOW] #16 Nomenclatura Ruim de Variáveis
File:        routes/report_routes.py:24-28
Description: Variáveis p1, p2, p3, p4, p5 para armazenar contagens de tasks por prioridade. Nomes de uma/duas letras sem nenhuma semântica — p1 pode ser qualquer coisa.
Impact:      Legibilidade severamente comprometida; o mapeamento p1→critical, p2→high, etc. não é evidente.
Recommendation: Renomear para priority_critical, priority_high, priority_medium, priority_low, priority_minimal.

[LOW] #16 Nomenclatura Ruim de Variáveis
File:        models/category.py:14
Description: Variável d = {} no método to_dict() da classe Category. Nome de uma letra sem semântica.
Impact:      Reduz legibilidade; não fica claro que d é o dicionário de retorno sendo construído.
Recommendation: Renomear para result.

[LOW] #16 Nomenclatura Ruim de Variáveis
File:        models/task.py:45
Description: Parâmetro p em validate_priority(self, p). Nome abreviado sem contexto — o que é p?
Impact:      Quem lê a assinatura do método não entende imediatamente o que é validado.
Recommendation: Renomear para value.

[LOW] #17 Código Morto
File:        routes/task_routes.py:7
Description: import json, os, sys, time — nenhum desses módulos é utilizado em task_routes.py.
Impact:      Imports desnecessários aumentam o tempo de carregamento do módulo e geram falsa impressão de dependências.
Recommendation: Remover a linha de import completa.

[LOW] #17 Código Morto
File:        routes/user_routes.py:6
Description: import hashlib, json, re — hashlib e json importados mas nunca chamados. Apenas re é utilizado (validação de email).
Impact:      Imports mortos poluem o namespace e confundem sobre as dependências reais do módulo.
Recommendation: Simplificar para import re.

[LOW] #17 Código Morto
File:        routes/report_routes.py:7
Description: from utils.helpers import format_date, calculate_percentage — ambas as funções são importadas mas nenhuma é chamada no arquivo; formatação de datas usa str() diretamente.
Impact:      Import morto; cria dependência falsa no módulo helpers.
Recommendation: Remover o import.

[LOW] #17 Código Morto
File:        utils/helpers.py:2-7
Description: Imports os, json, sys, math, hashlib no topo de helpers.py — nenhum deles é usado em qualquer função do arquivo.
Impact:      5 módulos carregados desnecessariamente; polui o namespace.
Recommendation: Remover todos os 5 imports não utilizados.

[LOW] #17 Código Morto
File:        utils/helpers.py:27-47, 49-83
Description: Funções generate_id(), is_valid_color() e process_task_data() definidas em helpers.py mas nunca chamadas por nenhum módulo do projeto (routes, controllers ou models).
Impact:      ~60 linhas de código morto que aumentam o tamanho do arquivo e criam confusão sobre o que está ativo.
Recommendation: Remover as três funções. Se process_task_data() for necessária futuramente, deve ser implementada com o contexto de uso claro.

================================
REFACTORING PRIORITY (LOW only)
================================
1. [LOW] Magic Numbers        — routes/task_routes.py → importar e usar constantes do helpers.py
2. [LOW] Magic Numbers        — routes/user_routes.py → importar MIN_PASSWORD_LENGTH, VALID_ROLES
3. [LOW] Nomenclatura Ruim    — routes/report_routes.py → renomear p1-p5
4. [LOW] Nomenclatura Ruim    — models/category.py → renomear d → result
5. [LOW] Nomenclatura Ruim    — models/task.py → renomear parâmetro p → value
6. [LOW] Código Morto         — routes/task_routes.py → remover imports json,os,sys,time
7. [LOW] Código Morto         — routes/user_routes.py → remover hashlib, json
8. [LOW] Código Morto         — routes/report_routes.py → remover import helpers
9. [LOW] Código Morto         — utils/helpers.py → remover imports e funções não usadas

================================
Total: 11 findings
Refactoring required: YES (LOW priority)
================================
