================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   ~14 analyzed | ~450 lines of code

================================
SUMMARY (LOW findings only — rodada de auditoria incremental)
================================
CRITICAL: - | HIGH: - | MEDIUM: - | LOW: 5
Total:    5 LOW findings

================================
FINDINGS
================================

--- LOW ---

[LOW] #15 Magic Numbers
File:        models.py:214-217
Description: Função relatorio_vendas() usa literais numéricos 10000, 5000, 1000 como thresholds de faturamento e 0.1, 0.05, 0.02 como multiplicadores de taxa de desconto, todos sem constantes nomeadas.
Impact:      Alterar qualquer taxa de desconto exige busca manual no código; o propósito dos valores não é autoexplicativo.
Recommendation: Extrair constantes DESCONTO_FATURAMENTO_ALTO, DESCONTO_FATURAMENTO_MEDIO, DESCONTO_FATURAMENTO_BAIXO, TAXA_DESCONTO_ALTO, TAXA_DESCONTO_MEDIO, TAXA_DESCONTO_BAIXO no topo do módulo.

[LOW] #16 Nomenclatura Ruim de Variáveis
File:        models.py:162-164, 186-190
Description: Cursors chamados cursor2 e cursor3 nas funções get_pedidos_usuario() e get_todos_pedidos(). Nomes não comunicam a finalidade: cursor2 busca itens do pedido, cursor3 busca o produto.
Impact:      Dificulta leitura e entendimento do fluxo de queries aninhadas. Aumenta custo cognitivo durante manutenção.
Recommendation: Renomear para itens_cursor e produto_cursor respectivamente.

[LOW] #16 Nomenclatura Ruim de Variáveis
File:        controllers.py:54, 152
Description: Variável id usada para capturar o retorno de models.criar_produto() (linha 54) e models.criar_usuario() (linha 152). O nome id é um builtin do Python, sobrescrever este nome é uma má prática.
Impact:      Pode mascarar bugs em contextos onde o builtin id() é necessário; reduz legibilidade.
Recommendation: Renomear para produto_id e usuario_id respectivamente.

[LOW] #17 Código Morto
File:        controllers.py:3
Description: Import from database import get_db presente mas não utilizado. Todas as operações de banco de dados são realizadas via funções do módulo models, nunca acessando get_db diretamente em controllers.py.
Impact:      Polui o namespace do módulo, gera confusão sobre dependências reais do arquivo.
Recommendation: Remover o import não utilizado.

================================
REFACTORING PRIORITY (LOW only)
================================
1. [LOW] Magic Numbers        — models.py → extrair constantes de desconto
2. [LOW] Nomenclatura Ruim    — models.py → renomear cursor2/cursor3
3. [LOW] Nomenclatura Ruim    — controllers.py → renomear variável id
4. [LOW] Código Morto         — controllers.py → remover import não usado

================================
Total: 5 findings
Refactoring required: YES (LOW priority)
================================
