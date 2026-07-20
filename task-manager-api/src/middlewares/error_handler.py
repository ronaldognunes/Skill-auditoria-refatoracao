from flask import jsonify


class AppError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({'error': e.message}), e.status_code

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Método não permitido'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Erro interno do servidor'}), 500
