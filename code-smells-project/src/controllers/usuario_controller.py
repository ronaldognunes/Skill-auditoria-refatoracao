from src.middlewares.error_handler import AppError
from src.models.usuario_model import UsuarioModel


class UsuarioController:
    def __init__(self):
        self.model = UsuarioModel()

    def listar(self) -> list:
        return self.model.find_all()

    def buscar_por_id(self, usuario_id: int) -> dict:
        usuario = self.model.find_by_id(usuario_id)
        if not usuario:
            raise AppError("Usuário não encontrado", 404)
        return usuario

    def criar(self, dados: dict) -> dict:
        if not dados:
            raise AppError("Dados inválidos", 400)
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            raise AppError("Nome, email e senha são obrigatórios", 400)
        usuario_id = self.model.create(nome, email, senha)
        return {"id": usuario_id}

    def login(self, dados: dict) -> dict:
        if not dados:
            raise AppError("Dados inválidos", 400)
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            raise AppError("Email e senha são obrigatórios", 400)
        # Playbook #6: busca por email (parametrizado) + comparação de hash
        row = self.model.find_by_email(email)
        if not row or not self.model.verify_password(row["senha"], senha):
            raise AppError("Email ou senha inválidos", 401)
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
