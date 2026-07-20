import logging
from flask import Flask, jsonify
from flask_cors import CORS

from src.config.settings import SECRET_KEY, DEBUG
from src.views.produto_routes import bp as produto_bp
from src.views.usuario_routes import bp as usuario_bp
from src.views.pedido_routes import bp as pedido_bp
from src.middlewares.error_handler import register_error_handlers

# Playbook LOW: logging estruturado substitui print() globais
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = Flask(__name__)
# Playbook #2: SECRET_KEY via variável de ambiente (não hardcoded)
app.config["SECRET_KEY"] = SECRET_KEY
CORS(app)

app.register_blueprint(produto_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(pedido_bp)

# Playbook #9: error handler centralizado registrado uma única vez
register_error_handlers(app)


@app.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@app.route("/health", methods=["GET"])
def health_check():
    from database import get_db
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    pedidos = cursor.fetchone()[0]
    # Segurança: sem secret_key, debug ou db_path na resposta
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
        "versao": "1.0.0",
    }), 200


# REMOVIDO: /admin/reset-db — endpoint destrutivo sem autenticação (CRITICAL)
# REMOVIDO: /admin/query  — execução arbitrária de SQL (CRITICAL)

if __name__ == "__main__":
    from database import get_db
    get_db()
    logging.info("=" * 50)
    logging.info("SERVIDOR INICIADO — http://localhost:5000")
    logging.info("=" * 50)
    # Playbook LOW: DEBUG controlado por variável de ambiente
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
