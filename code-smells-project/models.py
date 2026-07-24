from database import get_db
import sqlite3

# Constantes para cálculo de desconto em relatório
DESCONTO_FATURAMENTO_ALTO = 10000
DESCONTO_FATURAMENTO_MEDIO = 5000
DESCONTO_FATURAMENTO_BAIXO = 1000
TAXA_DESCONTO_ALTO = 0.10
TAXA_DESCONTO_MEDIO = 0.05
TAXA_DESCONTO_BAIXO = 0.02

def get_todos_produtos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    result = []
    for row in rows:

        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"]
        })
    return result

def get_produto_por_id(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"]
        }
    return None

def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('" +
        nome + "', '" + descricao + "', " + str(preco) + ", " + str(estoque) + ", '" + categoria + "')"
    )
    db.commit()
    return cursor.lastrowid

def atualizar_produto(id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = '" + nome + "', descricao = '" + descricao +
        "', preco = " + str(preco) + ", estoque = " + str(estoque) +
        ", categoria = '" + categoria + "' WHERE id = " + str(id)
    )
    db.commit()
    return True

def deletar_produto(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = " + str(id))
    db.commit()
    return True

def get_todos_usuarios():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "senha": row["senha"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        })
    return result

def get_usuario_por_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = " + str(id))
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "senha": row["senha"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        }
    return None

def login_usuario(email, senha):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
    )
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"]
        }
    return None

def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" +
        nome + "', '" + email + "', '" + senha + "', '" + tipo + "')"
    )
    db.commit()
    return cursor.lastrowid

def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    total = 0

    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total = total + (produto["preco"] * item["quantidade"])

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (" +
        str(usuario_id) + ", 'pendente', " + str(total) + ")"
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        cursor.execute("SELECT preco FROM produtos WHERE id = " + str(item["produto_id"]))
        produto = cursor.fetchone()
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (" +
            str(pedido_id) + ", " + str(item["produto_id"]) + ", " +
            str(item["quantidade"]) + ", " + str(produto["preco"]) + ")"
        )

        cursor.execute(
            "UPDATE produtos SET estoque = estoque - " + str(item["quantidade"]) +
            " WHERE id = " + str(item["produto_id"])
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}

def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": []
        }

        itens_cursor = db.cursor()
        itens_cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
        itens = itens_cursor.fetchall()
        for item in itens:
            produto_cursor = db.cursor()
            produto_cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
            prod = produto_cursor.fetchone()
            pedido["itens"].append({
                "produto_id": item["produto_id"],
                "produto_nome": prod["nome"] if prod else "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"]
            })
        result.append(pedido)
    return result

def get_todos_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos")
    rows = cursor.fetchall()
    result = []
    for row in rows:

        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": []
        }
        itens_cursor = db.cursor()
        itens_cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
        itens = itens_cursor.fetchall()
        for item in itens:
            produto_cursor = db.cursor()
            produto_cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
            prod = produto_cursor.fetchone()
            pedido["itens"].append({
                "produto_id": item["produto_id"],
                "produto_nome": prod["nome"] if prod else "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"]
            })
        result.append(pedido)
    return result

def relatorio_vendas():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0]
    if faturamento is None:
        faturamento = 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    desconto = 0
    if faturamento > DESCONTO_FATURAMENTO_ALTO:
        desconto = faturamento * TAXA_DESCONTO_ALTO
    elif faturamento > DESCONTO_FATURAMENTO_MEDIO:
        desconto = faturamento * TAXA_DESCONTO_MEDIO
    elif faturamento > DESCONTO_FATURAMENTO_BAIXO:
        desconto = faturamento * TAXA_DESCONTO_BAIXO

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
    }

def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE pedidos SET status = '" + novo_status + "' WHERE id = " + str(pedido_id)
    )
    db.commit()
    return True

def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM produtos WHERE 1=1"
    if termo:
        query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
    if categoria:
        query += " AND categoria = '" + categoria + "'"
    if preco_min:
        query += " AND preco >= " + str(preco_min)
    if preco_max:
        query += " AND preco <= " + str(preco_max)

    cursor.execute(query)
    rows = cursor.fetchall()
    result = []
    for row in rows:

        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"]
        })
    return result
