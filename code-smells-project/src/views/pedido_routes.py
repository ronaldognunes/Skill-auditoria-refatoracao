from flask import Blueprint, request, jsonify
from src.controllers.pedido_controller import PedidoController

bp = Blueprint("pedidos", __name__)
_controller = PedidoController()


@bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    resultado = _controller.criar(request.get_json())
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


@bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    return jsonify({"dados": _controller.listar_todos(), "sucesso": True}), 200


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": _controller.listar_por_usuario(usuario_id), "sucesso": True}), 200


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    _controller.atualizar_status(pedido_id, request.get_json())
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


@bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    return jsonify({"dados": _controller.relatorio(), "sucesso": True}), 200
