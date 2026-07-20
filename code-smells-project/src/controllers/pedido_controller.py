import logging
from src.middlewares.error_handler import AppError
from src.models.pedido_model import PedidoModel

logger = logging.getLogger(__name__)

STATUSES_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


class PedidoController:
    def __init__(self):
        self.model = PedidoModel()

    def criar(self, dados: dict) -> dict:
        if not dados:
            raise AppError("Dados inválidos", 400)
        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            raise AppError("Usuario ID é obrigatório", 400)
        if not itens:
            raise AppError("Pedido deve ter pelo menos 1 item", 400)
        resultado = self.model.create(usuario_id, itens)
        if "erro" in resultado:
            raise AppError(resultado["erro"], 400)
        # Playbook #5 + LOW: logging estruturado substitui print() e simulações de notificação
        logger.info("Pedido %s criado para usuario %s", resultado["pedido_id"], usuario_id)
        return resultado

    def listar_por_usuario(self, usuario_id: int) -> list:
        return self.model.find_by_usuario(usuario_id)

    def listar_todos(self) -> list:
        return self.model.find_all()

    def atualizar_status(self, pedido_id: int, dados: dict) -> None:
        if not dados:
            raise AppError("Dados inválidos", 400)
        novo_status = dados.get("status", "")
        if novo_status not in STATUSES_VALIDOS:
            raise AppError("Status inválido", 400)
        self.model.update_status(pedido_id, novo_status)
        if novo_status == "aprovado":
            logger.info("Pedido %s aprovado — preparar envio", pedido_id)
        elif novo_status == "cancelado":
            logger.info("Pedido %s cancelado — devolver estoque", pedido_id)

    def relatorio(self) -> dict:
        return self.model.relatorio()
