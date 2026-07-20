from database import get_db

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


class ProdutoModel:
    # Playbook #8: serialização extraída para helper reutilizável
    def _serialize(self, row) -> dict:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"],
        }

    def find_all(self) -> list:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE ativo = 1")
        return [self._serialize(row) for row in cursor.fetchall()]

    def find_by_id(self, produto_id: int) -> dict | None:
        db = get_db()
        cursor = db.cursor()
        # Playbook #3: query parametrizada
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return self._serialize(row) if row else None

    def search(self, termo: str, categoria=None, preco_min=None, preco_max=None) -> list:
        db = get_db()
        cursor = db.cursor()
        # Playbook #3: query dinâmica com parâmetros (sem concatenação)
        query = "SELECT * FROM produtos WHERE ativo = 1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params.extend([f"%{termo}%", f"%{termo}%"])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)
        cursor.execute(query, params)
        return [self._serialize(row) for row in cursor.fetchall()]

    def create(self, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        db.commit()
        return cursor.lastrowid

    def update(self, produto_id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> bool:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=?, categoria=? WHERE id=?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        db.commit()
        return True

    def delete(self, produto_id: int) -> bool:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        db.commit()
        return True
