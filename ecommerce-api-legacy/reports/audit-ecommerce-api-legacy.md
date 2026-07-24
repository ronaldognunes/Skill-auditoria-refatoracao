================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   ~15 analyzed | ~300 lines of code

================================
SUMMARY (LOW findings only — rodada de auditoria incremental)
================================
CRITICAL: - | HIGH: - | MEDIUM: - | LOW: 4
Total:    4 LOW findings

================================
FINDINGS
================================

--- LOW ---

[LOW] #15 Magic Numbers
File:        src/controllers/CheckoutController.js:32
Description: A validação do cartão usa card.startsWith('4') onde '4' é o prefixo BIN do cartão Visa. O literal string não tem constante nomeada explicando seu propósito.
Impact:      Se o critério de validação mudar (ex: suporte a outros prefixos), a busca global por '4' seria ambígua e propensa a falsos positivos.
Recommendation: Extrair constante VISA_CARD_PREFIX = '4' no topo do arquivo, antes de usar na comparação.

[LOW] #16 Nomenclatura Ruim de Variáveis
File:        database.js:28
Description: Coluna pass no schema SQL da tabela users. O nome é ambíguo — pode ser confundido com a palavra reservada em outras linguagens — e não deixa claro que armazena um hash de senha.
Impact:      Reduz legibilidade do schema; desenvolvedor precisa inferir que é um hash e não a senha em texto puro.
Recommendation: Renomear para password_hash tanto no CREATE TABLE (database.js) quanto no INSERT (UserModel.js).

[LOW] #17 Código Morto
File:        src/config/settings.js:3
Description: paymentGatewayKey é exportado via module.exports mas nunca é importado ou referenciado em nenhum controller, rota ou serviço do projeto.
Impact:      Export desnecessário polui o módulo de configuração e cria falsa impressão de que integração com gateway de pagamento está configurada.
Recommendation: Remover a propriedade paymentGatewayKey do objeto exportado.

[LOW] #17 Código Morto
File:        src/config/settings.js:4
Description: smtpUser é exportado mas nunca utilizado. O projeto não implementa envio de email em nenhuma rota ou controller.
Impact:      Configuração exportada sem uso gera ruído e confusão sobre o escopo real de funcionalidades do módulo.
Recommendation: Remover a propriedade smtpUser do objeto exportado.

================================
REFACTORING PRIORITY (LOW only)
================================
1. [LOW] Magic Numbers     — src/controllers/CheckoutController.js → extrair VISA_CARD_PREFIX
2. [LOW] Nomenclatura Ruim — database.js + UserModel.js → renomear coluna pass → password_hash
3. [LOW] Código Morto      — src/config/settings.js → remover paymentGatewayKey e smtpUser

================================
Total: 4 findings
Refactoring required: YES (LOW priority)
================================
