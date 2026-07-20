from flask import Blueprint, request, jsonify
from src.controllers.task_controller import TaskController
from src.middlewares.auth import token_required

task_bp = Blueprint('tasks', __name__)
_ctrl = TaskController()


@task_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks():
    return jsonify(_ctrl.list_tasks()), 200


@task_bp.route('/tasks/search', methods=['GET'])
@token_required
def search_tasks():
    return jsonify(_ctrl.search_tasks(
        q=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', '')
    )), 200


@task_bp.route('/tasks/stats', methods=['GET'])
@token_required
def task_stats():
    return jsonify(_ctrl.get_stats()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    return jsonify(_ctrl.get_task(task_id)), 200


@task_bp.route('/tasks', methods=['POST'])
@token_required
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_ctrl.create_task(data)), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(_ctrl.update_task(task_id, data)), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id):
    _ctrl.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200
