# Atualiza apenas os atributos de um ser (não altera params/img/gif)
def update_ser_atributos(ser_id, novos):
    init_db()
    con = duckdb.connect(DB_PATH)
    con.execute('''
        UPDATE seres SET nome=?, descricao=?, tipo1=?, tipo2=?, vida=?, poder=?, resistencia=?, sabedoria=?, espirito=?, impeto=? WHERE id=?
    ''', [
        novos['nome'], novos['descricao'], novos['tipo1'], novos['tipo2'],
        int(novos['vida']), int(novos['poder']), int(novos['resistencia']), int(novos['sabedoria']), int(novos['espirito']), int(novos['impeto']), ser_id
    ])
    con.close()
# Deleta um ser pelo id
def delete_ser(ser_id):
    init_db()
    con = duckdb.connect(DB_PATH)
    con.execute('DELETE FROM seres WHERE id=?', [ser_id])
    con.close()
# persistence.py
"""
Módulo de persistência para salvar e carregar entidades (Seres) com atributos, parâmetros, imagem e gif em DuckDB.
"""
import duckdb
import os
import io
from PIL import Image

DB_PATH = 'seres.duckdb'

# Inicializa o banco e tabela se não existir
def init_db():
    con = duckdb.connect(DB_PATH)
    con.execute('''
        CREATE TABLE IF NOT EXISTS seres (
            id BIGINT PRIMARY KEY,
            nome TEXT,
            descricao TEXT,
            tipo1 TEXT,
            tipo2 TEXT,
            vida INTEGER,
            poder INTEGER,
            resistencia INTEGER,
            sabedoria INTEGER,
            espirito INTEGER,
            impeto INTEGER,
            fractal_params BLOB,
            img BLOB,
            gif BLOB
        )
    ''')
    con.close()

# Salva um novo ser
# params: dict com todos os parâmetros do fractal
# img: PIL.Image
# gif_bytes: bytes do gif
# atributos: dict com os campos extras

def save_ser(nome, descricao, tipo1, tipo2, vida, poder, resistencia, sabedoria, espirito, impeto, params, img, gif_bytes):
    import pickle
    init_db()
    con = duckdb.connect(DB_PATH)
    # Gera id manualmente
    cur = con.execute('SELECT max(id) FROM seres')
    row = cur.fetchone()
    next_id = (row[0] or 0) + 1
    # Serializa imagem PNG
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    # Serializa params
    params_blob = pickle.dumps(params)
    con.execute('''
        INSERT INTO seres (id, nome, descricao, tipo1, tipo2, vida, poder, resistencia, sabedoria, espirito, impeto, fractal_params, img, gif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [next_id, nome, descricao, tipo1, tipo2, vida, poder, resistencia, sabedoria, espirito, impeto, params_blob, img_bytes, gif_bytes])
    con.close()

# Lista todos os seres
# Retorna lista de dicts

def list_seres():
    import pickle
    init_db()
    con = duckdb.connect(DB_PATH)
    rows = con.execute('SELECT id, nome, descricao, tipo1, tipo2, vida, poder, resistencia, sabedoria, espirito, impeto, fractal_params, img, gif FROM seres').fetchall()
    seres = []
    for row in rows:
        # params, img, gif podem ser None
        params = None
        img = None
        gif_bytes = None
        try:
            if row[11] is not None:
                params = pickle.loads(row[11])
        except Exception:
            params = None
        try:
            if row[12] is not None:
                img = Image.open(io.BytesIO(row[12]))
        except Exception:
            img = None
        if row[13] is not None:
            gif_bytes = row[13]
        seres.append({
            'id': row[0], 'nome': row[1], 'descricao': row[2], 'tipo1': row[3], 'tipo2': row[4],
            'vida': row[5], 'poder': row[6], 'resistencia': row[7], 'sabedoria': row[8], 'espirito': row[9], 'impeto': row[10],
            'params': params, 'img': img, 'gif_bytes': gif_bytes
        })
    con.close()
    return seres

# Carrega um ser pelo id (com imagem/gif/params)
def load_ser(id):
    import pickle
    init_db()
    con = duckdb.connect(DB_PATH)
    row = con.execute('SELECT nome, descricao, tipo1, tipo2, vida, poder, resistencia, sabedoria, espirito, impeto, fractal_params, img, gif FROM seres WHERE id=?', [id]).fetchone()
    if not row:
        return None
    params = pickle.loads(row[10])
    img = Image.open(io.BytesIO(row[11]))
    gif_bytes = row[12]
    ser = {
        'nome': row[0], 'descricao': row[1], 'tipo1': row[2], 'tipo2': row[3],
        'vida': row[4], 'poder': row[5], 'resistencia': row[6], 'sabedoria': row[7], 'espirito': row[8], 'impeto': row[9],
        'params': params, 'img': img, 'gif_bytes': gif_bytes
    }
    con.close()
    return ser

# Exemplo de uso:
# save_ser('Dragão', 'Ser mítico', 'Fogo', 'Voador', 100, 80, 70, 60, 50, 90, params, img, gif_bytes)
# seres = list_seres()
# ser = load_ser(1)
