from src.middlewares.error_handler import AppError
from src.models.produto_model import ProdutoModel, CATEGORIAS_VALIDAS


class ProdutoController:
    def __init__(self):
        self.model = ProdutoModel()

    # Playbook #8: validação extraída como helper — elimina duplicação entre criar/atualizar
    def _validate_dados(self, dados: dict) -> tuple:
        if not dados:
            raise AppError("Dados inválidos", 400)
        nome = dados.get("nome")
        preco = dados.get("preco")
        estoque = dados.get("estoque")
        if nome is None:
            raise AppError("Nome é obrigatório", 400)
        if preco is None:
            raise AppError("Preço é obrigatório", 400)
        if estoque is None:
            raise AppError("Estoque é obrigatório", 400)
        if not isinstance(preco, (int, float)) or preco < 0:
            raise AppError("Preço inválido", 400)
        if not isinstance(estoque, int) or estoque < 0:
            raise AppError("Estoque inválido", 400)
        if len(str(nome)) < 2:
            raise AppError("Nome muito curto", 400)
        if len(str(nome)) > 200:
            raise AppError("Nome muito longo", 400)
        categoria = dados.get("categoria", "geral")
        if categoria not in CATEGORIAS_VALIDAS:
            raise AppError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}", 400)
        return str(nome), dados.get("descricao", ""), float(preco), int(estoque), categoria

    def listar(self) -> list:
        return self.model.find_all()

    def buscar_por_id(self, produto_id: int) -> dict:
        produto = self.model.find_by_id(produto_id)
        if not produto:
            raise AppError("Produto não encontrado", 404)
        return produto

    def buscar(self, termo: str, categoria, preco_min, preco_max) -> list:
        try:
            preco_min = float(preco_min) if preco_min else None
            preco_max = float(preco_max) if preco_max else None
        except ValueError:
            raise AppError("Parâmetros de preço inválidos", 400)
        return self.model.search(termo, categoria, preco_min, preco_max)

    def criar(self, dados: dict) -> dict:
        nome, descricao, preco, estoque, categoria = self._validate_dados(dados)
        produto_id = self.model.create(nome, descricao, preco, estoque, categoria)
        return {"id": produto_id}

    def atualizar(self, produto_id: int, dados: dict) -> None:
        if not self.model.find_by_id(produto_id):
            raise AppError("Produto não encontrado", 404)
        nome, descricao, preco, estoque, categoria = self._validate_dados(dados)
        self.model.update(produto_id, nome, descricao, preco, estoque, categoria)

    def deletar(self, produto_id: int) -> None:
        if not self.model.find_by_id(produto_id):
            raise AppError("Produto não encontrado", 404)
        self.model.delete(produto_id)
