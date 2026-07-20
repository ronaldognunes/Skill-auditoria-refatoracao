from flask import Blueprint, request, jsonify
from src.controllers.produto_controller import ProdutoController

bp = Blueprint("produtos", __name__)
_controller = ProdutoController()


@bp.route("/produtos", methods=["GET"])
def listar_produtos():
    return jsonify({"dados": _controller.listar(), "sucesso": True}), 200


@bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    resultados = _controller.buscar(
        request.args.get("q", ""),
        request.args.get("categoria"),
        request.args.get("preco_min"),
        request.args.get("preco_max"),
    )
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    return jsonify({"dados": _controller.buscar_por_id(id), "sucesso": True}), 200


@bp.route("/produtos", methods=["POST"])
def criar_produto():
    resultado = _controller.criar(request.get_json())
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Produto criado"}), 201


@bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    _controller.atualizar(id, request.get_json())
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    _controller.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
