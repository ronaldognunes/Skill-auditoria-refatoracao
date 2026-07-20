from flask import Blueprint, request, jsonify
from src.controllers.usuario_controller import UsuarioController

bp = Blueprint("usuarios", __name__)
_controller = UsuarioController()


@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify({"dados": _controller.listar(), "sucesso": True}), 200


@bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    return jsonify({"dados": _controller.buscar_por_id(id), "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    resultado = _controller.criar(request.get_json())
    return jsonify({"dados": resultado, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    usuario = _controller.login(request.get_json())
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
