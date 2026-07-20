from flask import Blueprint, request, jsonify
from src.controllers.report_controller import ReportController
from src.controllers.category_controller import CategoryController
from src.middlewares.auth import token_required

report_bp = Blueprint('reports', __name__)
_report_ctrl = ReportController()
_category_ctrl = CategoryController()


@report_bp.route('/reports/summary', methods=['GET'])
@token_required
def summary_report():
    return jsonify(_report_ctrl.summary_report()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
@token_required
def user_report(user_id):
    return jsonify(_report_ctrl.user_report(user_id)), 200


@report_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    return jsonify(_category_ctrl.list_categories()), 200


@report_bp.route('/categories', methods=['POST'])
@token_required
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_category_ctrl.create_category(data)), 201


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@token_required
def update_category(cat_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_category_ctrl.update_category(cat_id, data)), 200


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@token_required
def delete_category(cat_id):
    _category_ctrl.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
