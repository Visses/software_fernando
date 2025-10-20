from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 🔹 Configuração da conexão com o MySQL
conexao = pymysql.connect(
   host='localhost',
    user='root',
    password='Nathan24$',  # use a senha que você criou
    db='lar_management',
    charset='utf8mb4',  # garante compatibilidade com acentuação
    cursorclass=pymysql.cursors.DictCursor
)

# 🔹 Rota inicial (home)
@app.route("/")
def index():
    return render_template("index.html")

def get_hospedes_count():
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT condicao, COUNT(*) as total
        FROM lar_alcina
        GROUP BY condicao
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    contagem = {'normal': 0, 'acamado': 0, 'especial': 0}
    for r in resultados:
        contagem[r['condicao']] = r['total']
    contagem['total'] = sum(contagem.values())

    return contagem


@app.route("/lar_alcina")
def lar_alcina():
    contagem = get_hospedes_count()

    # Pegar lista de hóspedes
    conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Nathan24$',
    database='lar_management',
    cursorclass=pymysql.cursors.DictCursor  # <<< ADICIONA ISSO
)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lar_alcina ORDER BY id DESC")

    hospedes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lar_alcina.html', contagem=contagem, hospedes=hospedes)






# Rota para processar o formulário
@app.route('/cadastrar_hospede', methods=['POST'])
def cadastrar_hospede():
    # Pegar todos os dados do formulário
    nome = request.form['nome']
    cpf = request.form['cpf']
    rg = request.form['rg']
    pais_vivos = request.form['pais_vivos']
    quantos_filhos = request.form.get('quantos_filhos')
    quantos_filhos = int(quantos_filhos) if quantos_filhos else 0


    condicao = request.form['condicao']
    possui_filhos = request.form['possui_filhos']
    possui_bens = request.form['possui_bens']
    estado_civil = request.form['estado_civil']
    profissao = request.form['profissao']
    numero_cadastro = request.form['numero_cadastro']
    data_ingresso = request.form['data_ingresso']  # date
    grau_dependencia = request.form['grau_dependencia']
    nascimento = request.form['nascimento']  # date
    cep = request.form['cep']
    endereco = request.form['endereco']
    uf = request.form['uf']
    tamanho_fralda = request.form['tamanho_fralda']
    referencia1 = request.form['referencia1']
    numero1 = request.form['numero1']
    referencia2 = request.form['referencia2']
    numero2 = request.form['numero2']
    referencia3 = request.form['referencia3']
    numero3 = request.form['numero3']
    diagnostico = request.form['diagnostico']
    historico = request.form['historico']

    # Conectar ao banco e inserir todos os campos
    conexao = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conexao.cursor()
    query = """
    INSERT INTO lar_alcina (
    nome, cpf, rg, condicao, possui_filhos, quantos_filhos, possui_bens, pais_vivos,
    estado_civil, profissao, numero_cadastro, data_ingresso, grau_dependencia,
    nascimento, cep, endereco, uf, tamanho_fralda,
    referencia1, numero1, referencia2, numero2, referencia3, numero3,
    diagnostico, historico
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

    cursor.execute(query, (
    nome, cpf, rg, condicao, possui_filhos, quantos_filhos, possui_bens, pais_vivos,
    estado_civil, profissao, numero_cadastro, data_ingresso, grau_dependencia,
    nascimento, cep, endereco, uf, tamanho_fralda,
    referencia1, numero1, referencia2, numero2, referencia3, numero3,
    diagnostico, historico
))
    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('lar_alcina'))  # redireciona de volta para o dashboard

# Ver ficha do hóspede (Lar Alcina)
@app.route("/lar_alcina/hospede/<int:hospede_id>")
def ver_ficha_alcina(hospede_id):
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lar_alcina WHERE id=%s", (hospede_id,))
    hospede = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if hospede is None:
        flash("Hóspede não encontrado.")
        return redirect(url_for('lar_alcina'))
    
    return render_template("ficha_hosp_alcina.html", hospede=hospede)

import os
from werkzeug.utils import secure_filename

# Caminho certo das fotos do Lar Alcina
UPLOAD_FOLDER = os.path.join("static", "uploads", "alcina", "fotos")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Garante que a pasta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/lar_alcina/editar_hospede/<int:hospede_id>", methods=["POST"])
def editar_hosp_alcina(hospede_id):
    dados = request.form
    foto = request.files.get('uploadFoto')

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Nathan24$',
        database='lar_management'
    )
    cursor = conn.cursor()

    foto_url = None

    # Se foi enviada nova foto
    if foto and allowed_file(foto.filename):
        filename = secure_filename(f"{hospede_id}_{foto.filename}")
        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        foto.save(caminho_salvar)
        # Caminho usado no HTML (relativo ao /static)
        foto_url = f"uploads/alcina/fotos/{filename}"

    # Monta query com foto opcional
    extra = ", foto_url=%s" if foto_url else ""
    query = f"""
        UPDATE lar_alcina SET 
            nome=%s,
            cpf=%s,
            rg=%s,
            condicao=%s,
            possui_filhos=%s,
            quantos_filhos=%s,
            possui_bens=%s,
            pais_vivos=%s,
            estado_civil=%s,
            profissao=%s,
            numero_cadastro=%s,
            data_ingresso=%s,
            grau_dependencia=%s,
            nascimento=%s,
            cep=%s,
            endereco=%s,
            uf=%s,
            tamanho_fralda=%s,
            referencia1=%s,
            numero1=%s,
            referencia2=%s,
            numero2=%s,
            referencia3=%s,
            numero3=%s,
            diagnostico=%s,
            historico=%s
            {extra}
        WHERE id=%s
    """

    valores = [
        dados['nome'], dados['cpf'], dados['rg'], dados['condicao'], dados['possui_filhos'],
        dados.get('quantos_filhos', 0),
        dados['possui_bens'], dados['pais_vivos'], dados['estado_civil'], dados['profissao'],
        dados['numero_cadastro'], dados['data_ingresso'], dados['grau_dependencia'], dados['nascimento'],
        dados['cep'], dados['endereco'], dados['uf'], dados['tamanho_fralda'],
        dados['referencia1'], dados['numero1'], dados['referencia2'], dados['numero2'],
        dados['referencia3'], dados['numero3'], dados['diagnostico'], dados['historico']
    ]

    if foto_url:
        valores.append(foto_url)

    valores.append(hospede_id)

    cursor.execute(query, valores)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('ver_ficha_alcina', hospede_id=hospede_id))


# Excluir hóspede (Lar Alcina)
@app.route("/lar_alcina/excluir_hospede/<int:hospede_id>", methods=["POST"])
def excluir_hosp_alcina(hospede_id):
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lar_alcina WHERE id=%s", (hospede_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('lar_alcina'))


























# 🔹 Função para contar hóspedes do Lar dos Idosos
def get_hospedes_count_idosos():
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT condicao, COUNT(*) as total
        FROM lar_idosos
        GROUP BY condicao
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    contagem = {'normal': 0, 'acamado': 0, 'especial': 0}
    for r in resultados:
        contagem[r['condicao']] = r['total']
    contagem['total'] = sum(contagem.values())

    return contagem


# 🔹 Rota para visualizar o dashboard do Lar dos Idosos
@app.route("/lar_idosos")
def lar_idosos():
    contagem = get_hospedes_count_idosos()

    # Pegar lista de hóspedes
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Nathan24$',
        database='lar_management',
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lar_idosos ORDER BY id DESC")

    hospedes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lar_idosos.html', contagem=contagem, hospedes=hospedes)


# 🔹 Rota para cadastrar hóspede no Lar dos Idosos
@app.route('/cadastrar_hosp_idosos', methods=['POST'])
def cadastrar_hosp_idosos():
    # Pegar todos os dados do formulário
    nome = request.form['nome']
    cpf = request.form['cpf']
    rg = request.form['rg']
    pais_vivos = request.form['pais_vivos']
    quantos_filhos = request.form.get('quantos_filhos')
    quantos_filhos = int(quantos_filhos) if quantos_filhos else 0

    condicao = request.form['condicao']
    possui_filhos = request.form['possui_filhos']
    possui_bens = request.form['possui_bens']
    estado_civil = request.form['estado_civil']
    profissao = request.form['profissao']
    numero_cadastro = request.form['numero_cadastro']
    data_ingresso = request.form['data_ingresso']
    grau_dependencia = request.form['grau_dependencia']
    nascimento = request.form['nascimento']
    cep = request.form['cep']
    endereco = request.form['endereco']
    uf = request.form['uf']
    tamanho_fralda = request.form['tamanho_fralda']
    referencia1 = request.form['referencia1']
    numero1 = request.form['numero1']
    referencia2 = request.form['referencia2']
    numero2 = request.form['numero2']
    referencia3 = request.form['referencia3']
    numero3 = request.form['numero3']
    diagnostico = request.form['diagnostico']
    historico = request.form['historico']

    # Inserir no banco lar_idosos
    conexao = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conexao.cursor()
    query = """
    INSERT INTO lar_idosos (
        nome, cpf, rg, condicao, possui_filhos, quantos_filhos, possui_bens, pais_vivos,
        estado_civil, profissao, numero_cadastro, data_ingresso, grau_dependencia,
        nascimento, cep, endereco, uf, tamanho_fralda,
        referencia1, numero1, referencia2, numero2, referencia3, numero3,
        diagnostico, historico
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        nome, cpf, rg, condicao, possui_filhos, quantos_filhos, possui_bens, pais_vivos,
        estado_civil, profissao, numero_cadastro, data_ingresso, grau_dependencia,
        nascimento, cep, endereco, uf, tamanho_fralda,
        referencia1, numero1, referencia2, numero2, referencia3, numero3,
        diagnostico, historico
    ))
    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('lar_idosos'))

# Upload
UPLOAD_FOLDER_IDOSOS = os.path.join("static", "uploads", "idosos", "fotos")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER_IDOSOS'] = UPLOAD_FOLDER_IDOSOS
os.makedirs(UPLOAD_FOLDER_IDOSOS, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ver ficha hóspede
@app.route("/lar_idosos/hospede/<int:hospede_id>")
def ver_ficha_idosos(hospede_id):
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lar_idosos WHERE id=%s", (hospede_id,))
    hospede = cursor.fetchone()
    cursor.close()
    conn.close()

    if hospede is None:
        flash("Hóspede não encontrado.")
        return redirect(url_for('lar_idosos_lista'))  # criar rota de lista de idosos

    return render_template("ficha_hosp_idosos.html", hospede=hospede)

# Editar hóspede
@app.route("/lar_idosos/editar_hospede/<int:hospede_id>", methods=["POST"])
def editar_hosp_idosos(hospede_id):
    dados = request.form
    foto = request.files.get('uploadFoto')

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    foto_url = None
    if foto and allowed_file(foto.filename):
        filename = secure_filename(f"{hospede_id}_{foto.filename}")
        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER_IDOSOS'], filename)
        foto.save(caminho_salvar)
        foto_url = f"uploads/idosos/fotos/{filename}"

    extra = ", foto_url=%s" if foto_url else ""

    query = f"""
        UPDATE lar_idosos SET 
            nome=%s, cpf=%s, rg=%s, condicao=%s, possui_filhos=%s, quantos_filhos=%s,
            possui_bens=%s, pais_vivos=%s, estado_civil=%s, profissao=%s,
            numero_cadastro=%s, data_ingresso=%s, grau_dependencia=%s, nascimento=%s,
            cep=%s, endereco=%s, uf=%s, tamanho_fralda=%s,
            referencia1=%s, numero1=%s, referencia2=%s, numero2=%s, referencia3=%s, numero3=%s,
            diagnostico=%s, historico=%s
            {extra}
        WHERE id=%s
    """

    valores = [
        dados['nome'], dados['cpf'], dados['rg'], dados['condicao'], dados['possui_filhos'],
        dados.get('quantos_filhos', 0), dados['possui_bens'], dados['pais_vivos'], dados['estado_civil'], dados['profissao'],
        dados['numero_cadastro'], dados['data_ingresso'], dados['grau_dependencia'], dados['nascimento'],
        dados['cep'], dados['endereco'], dados['uf'], dados['tamanho_fralda'],
        dados['referencia1'], dados['numero1'], dados['referencia2'], dados['numero2'],
        dados['referencia3'], dados['numero3'], dados['diagnostico'], dados['historico']
    ]

    if foto_url:
        valores.append(foto_url)
    valores.append(hospede_id)

    cursor.execute(query, valores)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('ver_ficha_idosos', hospede_id=hospede_id))

# Excluir hóspede
@app.route("/lar_idosos/excluir_hospede/<int:hospede_id>", methods=["POST"])
def excluir_hosp_idosos(hospede_id):
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lar_idosos WHERE id=%s", (hospede_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('lar_idosos'))  # criar rota de lista de idosos









@app.route("/estoque_fraldas")
def estoque_fraldas():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_fraldas")
    fraldas = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.tamanho, f.marca 
        FROM log_fraldas l 
        JOIN estoque_fraldas f ON l.fralda_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal (somente fraldas usadas / redução)
    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_fraldas
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()

    # Buscar log de alterações
    cursor.execute("""
        SELECT l.*, f.tamanho, f.marca,
               (SELECT ROUND(SUM(l2.quantidade)/COUNT(DISTINCT DATE_FORMAT(l2.data_hora,'%Y-%m')),2)
                FROM log_fraldas l2
                WHERE l2.fralda_id = l.fralda_id AND l2.acao IN ('aumento','redução','cadastro')
               ) AS media_mensal
        FROM log_fraldas l
        JOIN estoque_fraldas f ON l.fralda_id=f.id
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_fraldas")
    total_estoque = cursor.fetchone()['total_estoque'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_fraldas.html", 
        fraldas=fraldas, 
        log=log, 
        media_mensal=media_mensal,
        total_estoque=total_estoque
    )



@app.route("/cadastrar_fralda", methods=["POST"])
def cadastrar_fralda():
    dados = request.get_json()
    print("📦 Dados recebidos:", dados)  # <- linha de debug
    tamanho = dados["tamanho"]
    marca = dados["marca"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    # Inserir na tabela estoque
    cursor.execute("INSERT INTO estoque_fraldas (tamanho, marca, quantidade, criado_em) VALUES (%s,%s,%s,NOW())", (tamanho, marca, quantidade))
    fralda_id = cursor.lastrowid
    # Inserir no log
    cursor.execute("INSERT INTO log_fraldas (fralda_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())", (fralda_id, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# Aumentar ou reduzir quantidade
@app.route("/alterar_estoque_fralda", methods=["POST"])
def alterar_estoque_fralda():
    dados = request.get_json()
    fralda_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute("UPDATE estoque_fraldas SET quantidade = quantidade + %s WHERE id=%s", (quantidade, fralda_id))
        cursor.execute("INSERT INTO log_fraldas (fralda_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())", (fralda_id, quantidade))
    elif acao == "reduzir":
        cursor.execute("UPDATE estoque_fraldas SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s", (quantidade, fralda_id))
        cursor.execute("INSERT INTO log_fraldas (fralda_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())", (fralda_id, quantidade))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


# Excluir fralda
@app.route("/excluir_fralda", methods=["POST"])
def excluir_fralda():
    dados = request.get_json()
    fralda_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_fraldas WHERE id=%s", (fralda_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


# Excluir log (com senha)
@app.route("/excluir_log_fralda", methods=["POST"])
def excluir_log_fralda():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":  # 🔒 senha de segurança
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_fraldas WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/estoque_alimentos")
def estoque_alimentos():
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM estoque_alimentos")
    alimentos = cursor.fetchall()

    cursor.execute("""
        SELECT l.*, a.nome, a.marca 
        FROM log_alimentos l
        JOIN estoque_alimentos a ON l.alimento_id=a.id
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()

    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_alimentos
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()

    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_alimentos")
    total_estoque = cursor.fetchone()['total_estoque'] or 0

    cursor.close()
    conn.close()

    return render_template("estoque_alimentos.html", alimentos=alimentos, log=log, media_mensal=media_mensal, total_estoque=total_estoque)


@app.route("/cadastrar_alimento", methods=["POST"])
def cadastrar_alimento():
    dados = request.get_json()
    nome = dados["nome"]
    marca = dados["marca"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO estoque_alimentos (nome, marca, quantidade, criado_em) VALUES (%s,%s,%s,NOW())", (nome, marca, quantidade))
    alimento_id = cursor.lastrowid
    cursor.execute("INSERT INTO log_alimentos (alimento_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())", (alimento_id, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_alimento", methods=["POST"])
def alterar_estoque_alimento():
    dados = request.get_json()
    alimento_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    if acao=="aumentar":
        cursor.execute("UPDATE estoque_alimentos SET quantidade = quantidade + %s WHERE id=%s", (quantidade, alimento_id))
        cursor.execute("INSERT INTO log_alimentos (alimento_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())", (alimento_id, quantidade))
    elif acao=="reduzir":
        cursor.execute("UPDATE estoque_alimentos SET quantidade = GREATEST(quantidade - %s,0) WHERE id=%s", (quantidade, alimento_id))
        cursor.execute("INSERT INTO log_alimentos (alimento_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())", (alimento_id, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_alimento", methods=["POST"])
def excluir_alimento():
    dados = request.get_json()
    alimento_id = dados["id"]
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_alimentos WHERE id=%s", (alimento_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_log_alimento", methods=["POST"])
def excluir_log_alimento():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_alimentos WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})



@app.route("/estoque_higiene")
def estoque_higiene():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_higiene")
    produtos = cursor.fetchall()
    
    # Log de alterações com média mensal por produto
    cursor.execute("""
        SELECT l.*, p.nome,
               (SELECT ROUND(SUM(l2.quantidade)/COUNT(DISTINCT DATE_FORMAT(l2.data_hora,'%Y-%m')),2)
                FROM log_higiene l2
                WHERE l2.produto_id = l.produto_id AND l2.acao IN ('aumento','redução','cadastro')
               ) AS media_mensal
        FROM log_higiene l
        JOIN estoque_higiene p ON l.produto_id=p.id
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal (somente reduções)
    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_higiene
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()
    
    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_higiene")
    total_estoque = cursor.fetchone()['total_estoque'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_higiene.html",
        produtos=produtos,
        log=log,
        media_mensal=media_mensal,
        total_estoque=total_estoque
    )


@app.route("/cadastrar_higiene", methods=["POST"])
def cadastrar_higiene():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    
    # Inserir produto
    cursor.execute("INSERT INTO estoque_higiene (nome, quantidade, criado_em) VALUES (%s,%s,NOW())", (nome, quantidade))
    produto_id = cursor.lastrowid
    
    # Inserir no log
    cursor.execute("INSERT INTO log_higiene (produto_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())", (produto_id, quantidade))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_higiene", methods=["POST"])
def alterar_estoque_higiene():
    dados = request.get_json()
    produto_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute("UPDATE estoque_higiene SET quantidade = quantidade + %s WHERE id=%s", (quantidade, produto_id))
        cursor.execute("INSERT INTO log_higiene (produto_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())", (produto_id, quantidade))
    elif acao == "reduzir":
        cursor.execute("UPDATE estoque_higiene SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s", (quantidade, produto_id))
        cursor.execute("INSERT INTO log_higiene (produto_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())", (produto_id, quantidade))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_higiene", methods=["POST"])
def excluir_higiene():
    dados = request.get_json()
    produto_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_higiene WHERE id=%s", (produto_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_log_higiene", methods=["POST"])
def excluir_log_higiene():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_higiene WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})



@app.route("/estoque_remedios")
def estoque_remedios():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_remedios")
    remedios = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, r.nome,
               (SELECT ROUND(SUM(l2.quantidade)/COUNT(DISTINCT DATE_FORMAT(l2.data_hora,'%Y-%m')),2)
                FROM log_remedios l2
                WHERE l2.remedio_id = l.remedio_id AND l2.acao IN ('aumento','redução','cadastro')
               ) AS media_mensal
        FROM log_remedios l
        JOIN estoque_remedios r ON l.remedio_id=r.id
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal (somente usados / redução)
    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_remedios
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()

    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_remedios")
    total_estoque = cursor.fetchone()['total_estoque'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_remedios.html", 
        remedios=remedios, 
        log=log, 
        media_mensal=media_mensal,
        total_estoque=total_estoque
    )


@app.route("/cadastrar_remedio", methods=["POST"])
def cadastrar_remedio():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    
    # Inserir no estoque
    cursor.execute("INSERT INTO estoque_remedios (nome, quantidade, criado_em) VALUES (%s,%s,NOW())", (nome, quantidade))
    remedio_id = cursor.lastrowid
    
    # Inserir no log
    cursor.execute("INSERT INTO log_remedios (remedio_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())", (remedio_id, quantidade))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_remedio", methods=["POST"])
def alterar_estoque_remedio():
    dados = request.get_json()
    remedio_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute("UPDATE estoque_remedios SET quantidade = quantidade + %s WHERE id=%s", (quantidade, remedio_id))
        cursor.execute("INSERT INTO log_remedios (remedio_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())", (remedio_id, quantidade))
    elif acao == "reduzir":
        cursor.execute("UPDATE estoque_remedios SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s", (quantidade, remedio_id))
        cursor.execute("INSERT INTO log_remedios (remedio_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())", (remedio_id, quantidade))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_remedio", methods=["POST"])
def excluir_remedio():
    dados = request.get_json()
    remedio_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_remedios WHERE id=%s", (remedio_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_log_remedio", methods=["POST"])
def excluir_log_remedio():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_remedios WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})








@app.route("/estoque_escritorio")
def estoque_escritorio():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_escritorio")
    itens = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.nome 
        FROM log_escritorio l 
        JOIN estoque_escritorio f ON l.item_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal (somente itens usados / redução)
    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_escritorio
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()

    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_escritorio")
    total_estoque = cursor.fetchone()['total_estoque'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_escritorio.html", 
        itens=itens, 
        log=log, 
        media_mensal=media_mensal,
        total_estoque=total_estoque
    )


@app.route("/cadastrar_item_escritorio", methods=["POST"])
def cadastrar_item_escritorio():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    # Inserir na tabela estoque
    cursor.execute(
        "INSERT INTO estoque_escritorio (nome, quantidade, criado_em) VALUES (%s,%s,NOW())",
        (nome, quantidade)
    )
    item_id = cursor.lastrowid
    # Inserir no log
    cursor.execute(
        "INSERT INTO log_escritorio (item_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())",
        (item_id, quantidade)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_escritorio", methods=["POST"])
def alterar_estoque_escritorio():
    dados = request.get_json()
    item_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute(
            "UPDATE estoque_escritorio SET quantidade = quantidade + %s WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_escritorio (item_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())",
            (item_id, quantidade)
        )
    elif acao == "reduzir":
        cursor.execute(
            "UPDATE estoque_escritorio SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_escritorio (item_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())",
            (item_id, quantidade)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_item_escritorio", methods=["POST"])
def excluir_item_escritorio():
    dados = request.get_json()
    item_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_escritorio WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_log_escritorio", methods=["POST"])
def excluir_log_escritorio():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":  # 🔒 senha de segurança
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_escritorio WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})





@app.route("/estoque_limpeza")
def estoque_limpeza():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_limpeza")
    itens = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.nome 
        FROM log_limpeza l 
        JOIN estoque_limpeza f ON l.item_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal (somente itens usados / redução)
    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_limpeza
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()

    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_limpeza")
    total_estoque = cursor.fetchone()['total_estoque'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_limpeza.html", 
        itens=itens, 
        log=log, 
        media_mensal=media_mensal,
        total_estoque=total_estoque
    )


@app.route("/cadastrar_item_limpeza", methods=["POST"])
def cadastrar_item_limpeza():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estoque_limpeza (nome, quantidade, criado_em) VALUES (%s,%s,NOW())",
        (nome, quantidade)
    )
    item_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO log_limpeza (item_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())",
        (item_id, quantidade)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_limpeza", methods=["POST"])
def alterar_estoque_limpeza():
    dados = request.get_json()
    item_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute(
            "UPDATE estoque_limpeza SET quantidade = quantidade + %s WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_limpeza (item_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())",
            (item_id, quantidade)
        )
    elif acao == "reduzir":
        cursor.execute(
            "UPDATE estoque_limpeza SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_limpeza (item_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())",
            (item_id, quantidade)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_item_limpeza", methods=["POST"])
def excluir_item_limpeza():
    dados = request.get_json()
    item_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_limpeza WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_log_limpeza", methods=["POST"])
def excluir_log_limpeza():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_limpeza WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})





@app.route("/estoque_descartaveis")
def estoque_descartaveis():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_descartaveis")
    itens = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.nome 
        FROM log_descartaveis l 
        JOIN estoque_descartaveis f ON l.item_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal (somente itens usados / redução)
    cursor.execute("""
        SELECT DATE_FORMAT(data_hora, '%Y-%m') as mes, SUM(quantidade) as total_usado
        FROM log_descartaveis
        WHERE acao='redução'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    media_mensal = cursor.fetchall()

    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_descartaveis")
    total_estoque = cursor.fetchone()['total_estoque'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_descartaveis.html", 
        itens=itens, 
        log=log, 
        media_mensal=media_mensal,
        total_estoque=total_estoque
    )


@app.route("/cadastrar_item_descartaveis", methods=["POST"])
def cadastrar_item_descartaveis():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estoque_descartaveis (nome, quantidade, criado_em) VALUES (%s,%s,NOW())",
        (nome, quantidade)
    )
    item_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO log_descartaveis (item_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())",
        (item_id, quantidade)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_descartaveis", methods=["POST"])
def alterar_estoque_descartaveis():
    dados = request.get_json()
    item_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute(
            "UPDATE estoque_descartaveis SET quantidade = quantidade + %s WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_descartaveis (item_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())",
            (item_id, quantidade)
        )
    elif acao == "reduzir":
        cursor.execute(
            "UPDATE estoque_descartaveis SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_descartaveis (item_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())",
            (item_id, quantidade)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_item_descartaveis", methods=["POST"])
def excluir_item_descartaveis():
    dados = request.get_json()
    item_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_descartaveis WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_log_descartaveis", methods=["POST"])
def excluir_log_descartaveis():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_descartaveis WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})




# Estoque de Aparelhos Permanentes
@app.route("/estoque_aparelhos")
def estoque_aparelhos():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_aparelhos")
    aparelhos = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.nome 
        FROM log_aparelhos l 
        JOIN estoque_aparelhos f ON l.aparelho_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("estoque_aparelhos.html", aparelhos=aparelhos, log=log)


@app.route("/cadastrar_aparelho", methods=["POST"])
def cadastrar_aparelho():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    # Inserir no estoque
    cursor.execute(
        "INSERT INTO estoque_aparelhos (nome, quantidade, criado_em) VALUES (%s,%s,NOW())",
        (nome, quantidade)
    )
    aparelho_id = cursor.lastrowid

    # Inserir no log
    cursor.execute(
        "INSERT INTO log_aparelhos (aparelho_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())",
        (aparelho_id, quantidade)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_aparelho", methods=["POST"])
def alterar_estoque_aparelho():
    dados = request.get_json()
    aparelho_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute(
            "UPDATE estoque_aparelhos SET quantidade = quantidade + %s WHERE id=%s",
            (quantidade, aparelho_id)
        )
        cursor.execute(
            "INSERT INTO log_aparelhos (aparelho_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())",
            (aparelho_id, quantidade)
        )
    elif acao == "reduzir":
        cursor.execute(
            "UPDATE estoque_aparelhos SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s",
            (quantidade, aparelho_id)
        )
        cursor.execute(
            "INSERT INTO log_aparelhos (aparelho_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())",
            (aparelho_id, quantidade)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_aparelho", methods=["POST"])
def excluir_aparelho():
    dados = request.get_json()
    aparelho_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    # Excluir do estoque (log permanece ou pode excluir com CASCADE)
    cursor.execute("DELETE FROM estoque_aparelhos WHERE id=%s", (aparelho_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/excluir_log_aparelhos", methods=["POST"])
def excluir_log_aparelhos():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":  # senha de segurança
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', database='lar_management'
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_aparelhos WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True})




# Estoque de Recreação
@app.route("/estoque_recreacao")
def estoque_recreacao():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_recreacao")
    itens = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.nome 
        FROM log_recreacao l 
        JOIN estoque_recreacao f ON l.item_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("estoque_recreacao.html", itens=itens, log=log)


@app.route("/cadastrar_recreacao", methods=["POST"])
def cadastrar_recreacao():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    # Inserir no estoque
    cursor.execute(
        "INSERT INTO estoque_recreacao (nome, quantidade, criado_em) VALUES (%s,%s,NOW())",
        (nome, quantidade)
    )
    item_id = cursor.lastrowid

    # Inserir no log
    cursor.execute(
        "INSERT INTO log_recreacao (item_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())",
        (item_id, quantidade)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_recreacao", methods=["POST"])
def alterar_estoque_recreacao():
    dados = request.get_json()
    item_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute(
            "UPDATE estoque_recreacao SET quantidade = quantidade + %s WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_recreacao (item_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())",
            (item_id, quantidade)
        )
    elif acao == "reduzir":
        cursor.execute(
            "UPDATE estoque_recreacao SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_recreacao (item_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())",
            (item_id, quantidade)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_recreacao", methods=["POST"])
def excluir_recreacao():
    dados = request.get_json()
    item_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque_recreacao WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})



# Estoque de EPI
@app.route("/estoque_epi")
def estoque_epi():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_epi")
    itens = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.*, f.nome, f.tamanho 
        FROM log_epi l 
        JOIN estoque_epi f ON l.item_id=f.id 
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("estoque_epi.html", itens=itens, log=log)


@app.route("/cadastrar_epi", methods=["POST"])
def cadastrar_epi():
    dados = request.get_json()
    nome = dados["nome"]
    tamanho = dados.get("tamanho", "")
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    # Inserir no estoque
    cursor.execute(
        "INSERT INTO estoque_epi (nome, tamanho, quantidade, criado_em) VALUES (%s,%s,%s,NOW())",
        (nome, tamanho, quantidade)
    )
    item_id = cursor.lastrowid

    # Inserir no log
    cursor.execute(
        "INSERT INTO log_epi (item_id, acao, quantidade, data_hora) VALUES (%s,'cadastro',%s,NOW())",
        (item_id, quantidade)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/alterar_estoque_epi", methods=["POST"])
def alterar_estoque_epi():
    dados = request.get_json()
    item_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute(
            "UPDATE estoque_epi SET quantidade = quantidade + %s WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_epi (item_id, acao, quantidade, data_hora) VALUES (%s,'aumento',%s,NOW())",
            (item_id, quantidade)
        )
    elif acao == "reduzir":
        cursor.execute(
            "UPDATE estoque_epi SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s",
            (quantidade, item_id)
        )
        cursor.execute(
            "INSERT INTO log_epi (item_id, acao, quantidade, data_hora) VALUES (%s,'redução',%s,NOW())",
            (item_id, quantidade)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/excluir_epi", methods=["POST"])
def excluir_epi():
    dados = request.get_json()
    item_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque_epi WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/excluir_log_epi", methods=["POST"])
def excluir_log_epi():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_epi WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/excluir_log_recreacao", methods=["POST"])
def excluir_log_recreacao():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":  # você pode alterar a senha padrão aqui
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', database='lar_management'
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_recreacao WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True})


# Rota para visualizar o estoque de Folhas
@app.route("/estoque_folhas")
def estoque_folhas():
    conn = pymysql.connect(
        host='localhost', user='root', password='Nathan24$', 
        database='lar_management', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    # Estoque atual
    cursor.execute("SELECT * FROM estoque_folhas")
    itens = cursor.fetchall()
    
    # Log de alterações
    cursor.execute("""
        SELECT l.id AS log_id, l.item_id, l.acao, l.quantidade, l.data_hora,
               f.nome, f.setor
        FROM log_folhas l
        JOIN estoque_folhas f ON l.item_id = f.id
        ORDER BY l.data_hora DESC
    """)
    log = cursor.fetchall()
    
    # Média mensal por setor
    cursor.execute("""
        SELECT f.setor, DATE_FORMAT(l.data_hora,'%Y-%m') AS mes, 
               SUM(l.quantidade) AS total_usado,
               ROUND(SUM(l.quantidade)/COUNT(DISTINCT DATE_FORMAT(l.data_hora,'%Y-%m')),2) AS media_mensal
        FROM log_folhas l
        JOIN estoque_folhas f ON l.item_id = f.id
        WHERE l.acao='redução'
        GROUP BY f.setor, mes
        ORDER BY f.setor, mes DESC
    """)
    media_setor = cursor.fetchall()
    
    # Total estoque atual
    cursor.execute("SELECT SUM(quantidade) as total_estoque FROM estoque_folhas")
    total_estoque = cursor.fetchone()['total_estoque'] or 0

    cursor.close()
    conn.close()
    
    return render_template(
        "estoque_folhas.html", 
        itens=itens, 
        log=log, 
        media_setor=media_setor,
        total_estoque=total_estoque
    )

# Cadastro de folhas
@app.route("/cadastrar_folhas", methods=["POST"])
def cadastrar_folhas():
    dados = request.get_json()
    nome = dados["nome"]
    setor = dados["setor"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO estoque_folhas (nome,setor,quantidade,criado_em) VALUES (%s,%s,%s,NOW())", (nome, setor, quantidade))
    item_id = cursor.lastrowid
    cursor.execute("INSERT INTO log_folhas (item_id,acao,quantidade,data_hora) VALUES (%s,'cadastro',%s,NOW())", (item_id, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# Alterar quantidade
@app.route("/alterar_estoque_folhas", methods=["POST"])
def alterar_estoque_folhas():
    dados = request.get_json()
    item_id = dados["id"]
    acao = dados["acao"]
    quantidade = int(dados["quantidade"])

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute("UPDATE estoque_folhas SET quantidade = quantidade + %s WHERE id=%s", (quantidade, item_id))
        cursor.execute("INSERT INTO log_folhas (item_id,acao,quantidade,data_hora) VALUES (%s,'aumento',%s,NOW())", (item_id, quantidade))
    elif acao == "reduzir":
        cursor.execute("UPDATE estoque_folhas SET quantidade = GREATEST(quantidade - %s, 0) WHERE id=%s", (quantidade, item_id))
        cursor.execute("INSERT INTO log_folhas (item_id,acao,quantidade,data_hora) VALUES (%s,'redução',%s,NOW())", (item_id, quantidade))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# Excluir item
@app.route("/excluir_folhas", methods=["POST"])
def excluir_folhas():
    dados = request.get_json()
    item_id = dados["id"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_folhas WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# Excluir log com senha
@app.route("/excluir_log_folhas", methods=["POST"])
def excluir_log_folhas():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_folhas WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# Estoque Rouparia
@app.route("/estoque_rouparia")
def estoque_rouparia():
    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    # Estoque atual
    cursor.execute("SELECT * FROM estoque_rouparia")
    itens = cursor.fetchall()

    # Log de alterações
    cursor.execute("SELECT l.*, r.nome FROM log_rouparia l JOIN estoque_rouparia r ON l.rouparia_id=r.id ORDER BY l.data_hora DESC")
    log = cursor.fetchall()

    # Média semestral (somente reduções)
    cursor.execute("""
        SELECT 
            CONCAT(YEAR(data_hora), '-', LPAD(CEIL(MONTH(data_hora)/6), 2, '0')) AS semestre,
            SUM(quantidade) AS total_usado,
            ROUND(SUM(quantidade)/6,2) AS media_semestral
        FROM log_rouparia
        WHERE acao='reduzir'
        GROUP BY semestre
        ORDER BY semestre DESC
    """)
    media_semestral = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("estoque_rouparia.html", itens=itens, log=log, media_semestral=media_semestral)

# Cadastro
@app.route("/cadastrar_rouparia", methods=["POST"])
def cadastrar_rouparia():
    dados = request.get_json()
    nome = dados["nome"]
    quantidade = dados["quantidade"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO estoque_rouparia (nome, quantidade) VALUES (%s,%s)", (nome, quantidade))
    rouparia_id = cursor.lastrowid
    cursor.execute("INSERT INTO log_rouparia (rouparia_id, acao, quantidade) VALUES (%s,'cadastro',%s)", (rouparia_id, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# Alterar quantidade
@app.route("/alterar_estoque_rouparia", methods=["POST"])
def alterar_estoque_rouparia():
    dados = request.get_json()
    id = dados["id"]
    acao = dados["acao"]
    quantidade = dados["quantidade"]

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()

    if acao == "aumentar":
        cursor.execute("UPDATE estoque_rouparia SET quantidade=quantidade+%s WHERE id=%s", (quantidade, id))
    elif acao == "reduzir":
        cursor.execute("UPDATE estoque_rouparia SET quantidade=quantidade-%s WHERE id=%s", (quantidade, id))

    cursor.execute("INSERT INTO log_rouparia (rouparia_id, acao, quantidade) VALUES (%s,%s,%s)", (id, acao, quantidade))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route('/excluir_rouparia', methods=['POST'])
def excluir_rouparia():
    dados = request.get_json()  # ← Corrigido para JSON
    id = dados.get('id')        # ← Usa .get() para evitar KeyError

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Nathan24$',
        database='lar_management'
    )
    cursor = conn.cursor()

    try:
        # Exclui primeiro os registros do log vinculados
        cursor.execute("DELETE FROM log_rouparia WHERE rouparia_id = %s", (id,))
        # Agora exclui o item da tabela principal
        cursor.execute("DELETE FROM estoque_rouparia WHERE id = %s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Erro ao excluir:", e)
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': True})



# Excluir log com senha
@app.route("/excluir_log_rouparia", methods=["POST"])
def excluir_log_rouparia():
    dados = request.get_json()
    senha = dados.get("senha")
    log_id = dados["id"]

    if senha != "admin123":
        return jsonify({"success": False, "message": "Senha incorreta"})

    conn = pymysql.connect(host='localhost', user='root', password='Nathan24$', database='lar_management')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_rouparia WHERE id=%s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/nutricao")
def nutricao():
    return render_template("nutricao.html")

if __name__ == "__main__":
    app.run(debug=True)