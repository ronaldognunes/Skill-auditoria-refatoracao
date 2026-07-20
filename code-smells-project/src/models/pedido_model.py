from database import get_db


class PedidoModel:
    # Playbook #7 + #8: JOIN único elimina N+1; agrupamento extraído como helper
    def _build_pedidos_com_itens(self, rows) -> list:
        pedidos = {}
        for row in rows:
            pid = row["pedido_id"]
            if pid not in pedidos:
                pedidos[pid] = {
                    "id": pid,
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": [],
                }
            if row["item_id"]:
                pedidos[pid]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                })
        return list(pedidos.values())

    def find_by_usuario(self, usuario_id: int) -> list:
        db = get_db()
        cursor = db.cursor()
        # Playbook #7: JOIN substitui N+1 queries (antes: 1 + N + N*M queries)
        cursor.execute("""
            SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
                   ip.id AS item_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = ip.produto_id
            WHERE p.usuario_id = ?
            ORDER BY p.id
        """, (usuario_id,))
        return self._build_pedidos_com_itens(cursor.fetchall())

    def find_all(self) -> list:
        db = get_db()
        cursor = db.cursor()
        # Playbook #7: mesmo JOIN único para todos os pedidos
        cursor.execute("""
            SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
                   ip.id AS item_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = ip.produto_id
            ORDER BY p.id
        """)
        return self._build_pedidos_com_itens(cursor.fetchall())

    def create(self, usuario_id: int, itens: list) -> dict:
        db = get_db()
        cursor = db.cursor()
        total = 0

        # Validar estoque antes de inserir qualquer registro
        for item in itens:
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],))
            produto = cursor.fetchone()
            if produto is None:
                return {"erro": f"Produto {item['produto_id']} não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {produto['nome']}"}
            total += produto["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute("SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],))
            produto = cursor.fetchone()
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}

    def update_status(self, pedido_id: int, novo_status: str) -> bool:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id),
        )
        db.commit()
        return True

    def relatorio(self) -> dict:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0]

        desconto = 0
        if faturamento > 10000:
            desconto = faturamento * 0.1
        elif faturamento > 5000:
            desconto = faturamento * 0.05
        elif faturamento > 1000:
            desconto = faturamento * 0.02

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
