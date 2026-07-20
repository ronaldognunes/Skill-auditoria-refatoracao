from flask import Blueprint, request, jsonify
from src.controllers.user_controller import UserController
from src.middlewares.auth import token_required

user_bp = Blueprint('users', __name__)
_ctrl = UserController()


@user_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    return jsonify(_ctrl.list_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    return jsonify(_ctrl.get_user(user_id)), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_ctrl.create_user(data)), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_ctrl.update_user(user_id, data)), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    _ctrl.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
@token_required
def get_user_tasks(user_id):
    return jsonify(_ctrl.get_user_tasks(user_id)), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_ctrl.login(data)), 200
