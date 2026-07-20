import logging
from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"erro": e.message, "sucesso": False}), e.status_code

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Erro interno do servidor")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
