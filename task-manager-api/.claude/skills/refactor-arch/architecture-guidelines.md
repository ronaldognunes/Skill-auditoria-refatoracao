# Architecture Guidelines: MVC Target Structure

Este documento define a estrutura MVC alvo para cada tecnologia suportada.

Use estas diretrizes como referência ao criar a nova estrutura na Fase 3.

---

## Python / Flask — Estrutura MVC Alvo

```
src/
├── config/
│   └── settings.py              ← Todas as configurações via os.getenv()
├── models/
│   └── <entity>_model.py        ← Classe do modelo + acesso a dados (queries)
├── controllers/
│   └── <entity>_controller.py   ← Lógica de negócio pura (sem HTTP)
├── views/
│   └── routes.py                ← Apenas roteamento HTTP, sem lógica
├── middlewares/
│   └── error_handler.py         ← Error handler centralizado
└── app.py                       ← Composition root: registra blueprints e middlewares
```

### Regras Python/Flask

1. **config/settings.py** — Nunca use valores hardcoded. Sempre use `os.getenv('VAR', 'default')`.
   ```python
   import os
   DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
   SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-key')
   DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
   ```

2. **models/<entity>_model.py** — Contém a classe do modelo e métodos de acesso a dados.
   - Usa queries parametrizadas (nunca concatenação de strings)
   - Não contém lógica de negócio
   - Não importa Flask (`request`, `jsonify`, etc.)
   ```python
   class ProductModel:
       def find_by_id(self, product_id: int) -> dict:
           cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
           return cursor.fetchone()
   ```

3. **controllers/<entity>_controller.py** — Contém lógica de negócio pura.
   - Não acessa banco diretamente (usa model)
   - Não importa Flask (`request`, `jsonify`, etc.)
   - Recebe dados Python simples, retorna dados Python simples
   ```python
   class ProductController:
       def __init__(self):
           self.model = ProductModel()

       def get_product(self, product_id: int) -> dict:
           product = self.model.find_by_id(product_id)
           if not product:
               raise ValueError(f"Product {product_id} not found")
           return product
   ```

4. **views/routes.py** — Apenas roteamento HTTP. Handler de rota deve ter no máximo 10 linhas.
   - Extrai dados do request
   - Chama controller
   - Formata resposta HTTP
   ```python
   @bp.route('/products/<int:product_id>', methods=['GET'])
   def get_product(product_id):
       try:
           product = controller.get_product(product_id)
           return jsonify(product), 200
       except ValueError as e:
           return jsonify({'error': str(e)}), 404
   ```

5. **middlewares/error_handler.py** — Error handler registrado globalmente.
   ```python
   def register_error_handlers(app):
       @app.errorhandler(404)
       def not_found(e):
           return jsonify({'error': 'Not found'}), 404

       @app.errorhandler(500)
       def internal_error(e):
           return jsonify({'error': 'Internal server error'}), 500
   ```

6. **app.py** — Composition root mínimo.
   ```python
   from flask import Flask
   from src.config.settings import SECRET_KEY, DEBUG
   from src.views.routes import bp
   from src.middlewares.error_handler import register_error_handlers

   app = Flask(__name__)
   app.secret_key = SECRET_KEY
   app.register_blueprint(bp)
   register_error_handlers(app)

   if __name__ == '__main__':
       app.run(debug=DEBUG)
   ```

---

## Node.js / Express — Estrutura MVC Alvo

```
src/
├── config/
│   └── settings.js              ← Configurações via process.env
├── models/
│   └── <Entity>Model.js         ← Acesso a dados (queries parametrizadas)
├── controllers/
│   └── <Entity>Controller.js    ← Lógica de negócio (async/await)
├── routes/
│   └── <entity>Routes.js        ← Apenas roteamento HTTP
├── middlewares/
│   └── errorHandler.js          ← Error handler centralizado
└── app.js                       ← Composition root
```

### Regras Node.js/Express

1. **config/settings.js** — Usa variáveis de ambiente via `process.env`.
   ```javascript
   module.exports = {
     dbPath: process.env.DB_PATH || './dev.db',
     jwtSecret: process.env.JWT_SECRET || 'dev-secret',
     paymentKey: process.env.PAYMENT_GATEWAY_KEY,
     port: parseInt(process.env.PORT) || 3000,
   };
   ```

2. **models/<Entity>Model.js** — Acesso a dados com queries parametrizadas.
   ```javascript
   class ProductModel {
     async findById(id) {
       return new Promise((resolve, reject) => {
         db.get('SELECT * FROM products WHERE id = ?', [id], (err, row) => {
           if (err) reject(err);
           else resolve(row);
         });
       });
     }
   }
   ```

3. **controllers/<Entity>Controller.js** — Lógica de negócio com async/await.
   ```javascript
   class ProductController {
     async getProduct(req, res, next) {
       try {
         const product = await this.model.findById(req.params.id);
         if (!product) return res.status(404).json({ error: 'Not found' });
         res.json(product);
       } catch (err) {
         next(err);
       }
     }
   }
   ```

4. **routes/<entity>Routes.js** — Apenas roteamento, sem lógica.
   ```javascript
   const router = require('express').Router();
   const ProductController = require('../controllers/ProductController');
   const controller = new ProductController();

   router.get('/:id', (req, res, next) => controller.getProduct(req, res, next));

   module.exports = router;
   ```

5. **middlewares/errorHandler.js** — Middleware de erro centralizado (4 parâmetros).
   ```javascript
   function errorHandler(err, req, res, next) {
     console.error(err.stack);
     res.status(err.status || 500).json({
       error: err.message || 'Internal Server Error'
     });
   }
   module.exports = errorHandler;
   ```

6. **app.js** — Composition root com middleware de erro no final.
   ```javascript
   const express = require('express');
   const { port } = require('./config/settings');
   const productRoutes = require('./routes/productRoutes');
   const errorHandler = require('./middlewares/errorHandler');

   const app = express();
   app.use(express.json());
   app.use('/api/products', productRoutes);
   app.use(errorHandler); // DEVE ser o último middleware

   app.listen(port, () => console.log(`Server running on port ${port}`));
   module.exports = app;
   ```

---

## Invariantes (válidas para ambas as stacks)

| Regra | Python/Flask | Node.js/Express |
|---|---|---|
| Sem hardcode de credenciais | `os.getenv()` | `process.env` |
| Queries parametrizadas | `execute("...", (val,))` | `query("...", [val])` |
| Hash de senha seguro | `werkzeug.security` ou `bcrypt` | `bcrypt` npm |
| Lógica de negócio isolada | `controllers/` | `controllers/` |
| Error handler centralizado | `register_error_handlers(app)` | `app.use(errorHandler)` |
| Debug desabilitado em prod | `DEBUG=false` via env | `NODE_ENV=production` |
