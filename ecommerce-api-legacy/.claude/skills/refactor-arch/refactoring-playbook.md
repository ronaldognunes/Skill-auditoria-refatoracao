# Refactoring Playbook

9 padrões de transformação com exemplos before/after para os anti-patterns mais comuns.

---

## Padrão 1: God Class → MVC Split

**Anti-Pattern:** God Class / God Method
**Quando aplicar:** Arquivo único >200 linhas com responsabilidades de model, controller e route misturadas.

### Before (Python/Flask — monolítico)
```python
# app.py — tudo misturado
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE active = 1")
    products = cursor.fetchall()
    # lógica de negócio aqui
    result = [{'id': p[0], 'name': p[1], 'price': p[2] * 1.1} for p in products]
    return jsonify(result)
```

### After (MVC Split)
```python
# src/models/product_model.py
class ProductModel:
    def find_active(self) -> list:
        cursor.execute("SELECT id, name, price FROM products WHERE active = 1")
        return cursor.fetchall()

# src/controllers/product_controller.py
class ProductController:
    def __init__(self):
        self.model = ProductModel()

    def list_products(self) -> list:
        products = self.model.find_active()
        return [{'id': p[0], 'name': p[1], 'price': p[2] * 1.1} for p in products]

# src/views/routes.py
@bp.route('/products', methods=['GET'])
def get_products():
    controller = ProductController()
    return jsonify(controller.list_products()), 200
```

---

## Padrão 2: Hardcoded Config → Settings Module

**Anti-Pattern:** Hardcoded Credentials
**Quando aplicar:** Qualquer credencial, chave ou configuração embutida no código.

### Before (Python)
```python
# app.py
app.secret_key = "minha-chave-super-secreta"
DB_PASSWORD = "admin123"
PAYMENT_KEY = "pk_live_abc123xyz"
SMTP_USER = "app@gmail.com"
SMTP_PASS = "senha-do-email"
```

### After (Python)
```python
# src/config/settings.py
import os
SECRET_KEY = os.getenv('SECRET_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
PAYMENT_KEY = os.getenv('PAYMENT_GATEWAY_KEY')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')

# .env (não commitar — adicionar ao .gitignore)
SECRET_KEY=minha-chave-super-secreta
DB_PASSWORD=admin123
PAYMENT_GATEWAY_KEY=pk_live_abc123xyz

# app.py
from src.config.settings import SECRET_KEY
app.secret_key = SECRET_KEY
```

### Before (Node.js)
```javascript
// utils.js
const paymentGatewayKey = 'sk_live_abc123';
const dbPass = 'admin123';
const smtpUser = 'app@gmail.com';
```

### After (Node.js)
```javascript
// src/config/settings.js
module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  dbPass: process.env.DB_PASSWORD,
  smtpUser: process.env.SMTP_USER,
};

// .env
PAYMENT_GATEWAY_KEY=sk_live_abc123
DB_PASSWORD=admin123
```

---

## Padrão 3: SQL Injection → Parameterized Queries

**Anti-Pattern:** SQL Injection
**Quando aplicar:** Qualquer query com concatenação de string ou f-string com variáveis.

### Before (Python — inseguro)
```python
# Vulnerável a SQL Injection
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)

def search_products(name):
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{name}%'")

def login(username, password):
    cursor.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password))
```

### After (Python — seguro)
```python
# Queries parametrizadas — o driver escapa os valores automaticamente
def get_user(user_id: int):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

def search_products(name: str):
    cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{name}%',))

def login(username: str, password_hash: str):
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
```

### Before (Node.js — inseguro)
```javascript
db.query(`SELECT * FROM users WHERE id = ${userId}`);
db.query("SELECT * FROM users WHERE email = '" + email + "'");
```

### After (Node.js — seguro)
```javascript
db.query('SELECT * FROM users WHERE id = ?', [userId]);
db.query('SELECT * FROM users WHERE email = ?', [email]);
```

---

## Padrão 4: Callback Hell → Async/Await

**Anti-Pattern:** Callback Hell (Node.js)
**Quando aplicar:** Callbacks aninhados com 3+ níveis de profundidade.

### Before (Callback Hell)
```javascript
db.get('SELECT * FROM users WHERE id = ?', [userId], function(err, user) {
  if (err) return res.status(500).json({error: err.message});
  db.all('SELECT * FROM orders WHERE user_id = ?', [user.id], function(err2, orders) {
    if (err2) return res.status(500).json({error: err2.message});
    orders.forEach(function(order) {
      db.all('SELECT * FROM items WHERE order_id = ?', [order.id], function(err3, items) {
        if (err3) return res.status(500).json({error: err3.message});
        // processa items...
      });
    });
  });
});
```

### After (Async/Await)
```javascript
// Promisify queries
const dbGet = (sql, params) => new Promise((resolve, reject) =>
  db.get(sql, params, (err, row) => err ? reject(err) : resolve(row))
);
const dbAll = (sql, params) => new Promise((resolve, reject) =>
  db.all(sql, params, (err, rows) => err ? reject(err) : resolve(rows))
);

// Handler limpo com async/await
async function getOrdersWithItems(req, res) {
  try {
    const user = await dbGet('SELECT * FROM users WHERE id = ?', [req.params.userId]);
    const orders = await dbAll('SELECT * FROM orders WHERE user_id = ?', [user.id]);
    const ordersWithItems = await Promise.all(
      orders.map(async order => ({
        ...order,
        items: await dbAll('SELECT * FROM items WHERE order_id = ?', [order.id])
      }))
    );
    res.json(ordersWithItems);
  } catch (err) {
    next(err);
  }
}
```

---

## Padrão 5: Heavy Route Handler → Controller

**Anti-Pattern:** Business Logic in Controller/Route Handler
**Quando aplicar:** Handler de rota >50 linhas ou com lógica de negócio complexa.

### Before (Flask — handler pesado)
```python
@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    user_id = data.get('user_id')
    cart_items = data.get('items', [])

    # lógica de negócio no handler
    total = 0
    for item in cart_items:
        cursor.execute("SELECT price FROM products WHERE id = ?", (item['id'],))
        product = cursor.fetchone()
        total += product['price'] * item['quantity']

    # desconto de negócio
    if total > 100:
        total = total * 0.9

    # salvar pedido
    cursor.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))
    order_id = cursor.lastrowid

    return jsonify({'order_id': order_id, 'total': total}), 201
```

### After (Flask — handler delegando para controller)
```python
# src/controllers/order_controller.py
class OrderController:
    def create_order(self, user_id: int, cart_items: list) -> dict:
        total = self._calculate_total(cart_items)
        total = self._apply_discounts(total)
        order_id = self.order_model.create(user_id, total)
        return {'order_id': order_id, 'total': total}

    def _calculate_total(self, cart_items: list) -> float:
        total = 0
        for item in cart_items:
            product = self.product_model.find_by_id(item['id'])
            total += product['price'] * item['quantity']
        return total

    def _apply_discounts(self, total: float) -> float:
        return total * 0.9 if total > 100 else total

# src/views/routes.py
@bp.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    result = order_controller.create_order(data['user_id'], data['items'])
    return jsonify(result), 201
```

---

## Padrão 6: Plaintext/Weak Password → Bcrypt

**Anti-Pattern:** Plaintext/Weak Password Storage
**Quando aplicar:** MD5, SHA1, texto puro, ou criptografia customizada para senhas.

### Before (Python — inseguro)
```python
import hashlib

def create_user(username, password):
    # MD5 é quebrável com rainbow tables
    password_hash = hashlib.md5(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (username, password_hash))

def verify_password(stored_hash, provided_password):
    return stored_hash == hashlib.md5(provided_password.encode()).hexdigest()
```

### After (Python — seguro)
```python
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, password):
    # bcrypt com salt automático
    password_hash = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                   (username, password_hash))

def verify_password(stored_hash, provided_password):
    return check_password_hash(stored_hash, provided_password)
```

### Before (Node.js — inseguro)
```javascript
function badCrypto(text) {
    return Buffer.from(text).toString('base64').substring(0, 10);
}
const passwordHash = badCrypto(password);
```

### After (Node.js — seguro)
```javascript
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;

async function hashPassword(password) {
    return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password, hash) {
    return bcrypt.compare(password, hash);
}
```

---

## Padrão 7: N+1 Query → JOIN

**Anti-Pattern:** N+1 Query Problem
**Quando aplicar:** Query dentro de loop for/forEach.

### Before (Python — N+1)
```python
def get_orders_with_items():
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    result = []
    for order in orders:
        # N queries adicionais para N pedidos
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order['id'],))
        items = cursor.fetchall()
        result.append({**order, 'items': items})
    return result
```

### After (Python — JOIN único)
```python
def get_orders_with_items():
    cursor.execute("""
        SELECT o.id, o.user_id, o.total,
               i.id as item_id, i.product_id, i.quantity, i.price
        FROM orders o
        LEFT JOIN order_items i ON i.order_id = o.id
        ORDER BY o.id
    """)
    rows = cursor.fetchall()

    # Agrupa items por pedido em Python
    orders = {}
    for row in rows:
        if row['id'] not in orders:
            orders[row['id']] = {
                'id': row['id'], 'user_id': row['user_id'],
                'total': row['total'], 'items': []
            }
        if row['item_id']:
            orders[row['id']]['items'].append({
                'id': row['item_id'], 'product_id': row['product_id'],
                'quantity': row['quantity'], 'price': row['price']
            })
    return list(orders.values())
```

---

## Padrão 8: Code Duplication → Helper/Service

**Anti-Pattern:** Code Duplication
**Quando aplicar:** Bloco de lógica idêntico em 2+ funções.

### Before (Python — duplicado)
```python
def get_user_tasks(user_id):
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    return [t for t in tasks if t['due_date'] < datetime.now().date()]  # duplicado

def get_overdue_report():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    return [t for t in tasks if t['due_date'] < datetime.now().date()]  # duplicado

def get_category_tasks(category_id):
    cursor.execute("SELECT * FROM tasks WHERE category_id = ?", (category_id,))
    tasks = cursor.fetchall()
    return [t for t in tasks if t['due_date'] < datetime.now().date()]  # duplicado
```

### After (Python — helper extraído)
```python
# src/controllers/task_controller.py
def is_overdue(task: dict) -> bool:
    """Retorna True se a tarefa está vencida."""
    return task['due_date'] < datetime.now().date()

def filter_overdue(tasks: list) -> list:
    return [t for t in tasks if is_overdue(t)]

def get_user_tasks(user_id):
    tasks = self.model.find_by_user(user_id)
    return filter_overdue(tasks)

def get_overdue_report():
    tasks = self.model.find_all()
    return filter_overdue(tasks)

def get_category_tasks(category_id):
    tasks = self.model.find_by_category(category_id)
    return filter_overdue(tasks)
```

---

## Padrão 9: No Error Handling → Centralized Handler

**Anti-Pattern:** Missing/Scattered Error Handling
**Quando aplicar:** Bare `except:`, ausência de error handler, ou tratamento de erro repetido em cada handler.

### Before (Python — sem tratamento centralizado)
```python
@app.route('/users/<id>')
def get_user(id):
    try:
        user = get_user_from_db(id)
        return jsonify(user)
    except Exception:  # bare except — captura até SystemExit
        return "Error", 500

@app.route('/products')
def get_products():
    try:
        products = get_products_from_db()
        return jsonify(products)
    except:  # repetido em todo handler
        return "Error", 500
```

### After (Python — error handler centralizado)
```python
# src/middlewares/error_handler.py
class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({'error': e.message}), e.status_code

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

# src/views/routes.py — handlers limpos, sem try/except repetido
@bp.route('/users/<int:user_id>')
def get_user(user_id):
    user = user_controller.get_user(user_id)  # lança AppError(404) se não encontrado
    return jsonify(user), 200

# app.py — registra uma única vez
from src.middlewares.error_handler import register_error_handlers
register_error_handlers(app)
```

### After (Node.js — error handler centralizado)
```javascript
// src/middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
  const status = err.status || 500;
  const message = err.message || 'Internal Server Error';
  res.status(status).json({ error: message });
}
module.exports = errorHandler;

// app.js — deve ser o ÚLTIMO middleware registrado
const errorHandler = require('./middlewares/errorHandler');
app.use(errorHandler);

// controllers — usam next(err) para propagar erros
async function getUser(req, res, next) {
  try {
    const user = await userModel.findById(req.params.id);
    if (!user) return next({ status: 404, message: 'User not found' });
    res.json(user);
  } catch (err) {
    next(err);
  }
}
```
