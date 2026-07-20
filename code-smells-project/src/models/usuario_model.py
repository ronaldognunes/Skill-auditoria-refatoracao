from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


class UsuarioModel:
    # Playbook #6 + segurança: nunca expõe o campo senha nas respostas
    def _serialize_public(self, row) -> dict:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"],
        }

    def find_all(self) -> list:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios")
        return [self._serialize_public(row) for row in cursor.fetchall()]

    def find_by_id(self, usuario_id: int) -> dict | None:
        db = get_db()
        cursor = db.cursor()
        # Playbook #3: query parametrizada
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return self._serialize_public(row) if row else None

    def find_by_email(self, email: str):
        db = get_db()
        cursor = db.cursor()
        # Playbook #3: query parametrizada
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()

    def create(self, nome: str, email: str, senha: str, tipo: str = "cliente") -> int:
        db = get_db()
        cursor = db.cursor()
        # Playbook #6: hash bcrypt via werkzeug antes de persistir
        senha_hash = generate_password_hash(senha)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        db.commit()
        return cursor.lastrowid

    def verify_password(self, stored_hash: str, senha: str) -> bool:
        # Playbook #6: comparação segura de hash
        return check_password_hash(stored_hash, senha)
