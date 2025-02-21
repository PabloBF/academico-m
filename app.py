from flask import Flask, render_template, redirect, request, flash, g
import mysql.connector
from mysql.connector import Error  # Importando a classe de erro corretamente

app = Flask(__name__)
app.config['SECRET_KEY'] = 'matheusfce'

DB_CONFIG = {
    'host': 'localhost',
    'database': 'ProfEduDB',
    'user': 'root',
    'password': 'senha'
}

def get_db_connection():
    """Obtém a conexão do banco, reutilizando-a se já existir na requisição."""
    if 'db_connection' not in g:
        try:
            g.db_connection = mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            flash(f"Erro ao conectar ao banco de dados: {e}", 'danger')
            g.db_connection = None
    return g.db_connection

@app.teardown_appcontext
def close_db_connection(exception=None):
    """Fecha a conexão do banco de dados ao final da requisição."""
    connection = g.pop('db_connection', None)
    if connection is not None and connection.is_connected():
        connection.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cadastro-professor', methods=['GET', 'POST'])
def cadastro_professor():
    """Renderiza a página de cadastro de professores e processa inserções no banco."""
    habilitacoes = []
    connection = get_db_connection()

    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Habilitacoes")
                habilitacoes = cursor.fetchall()
        except Error as err:
            flash(f"Erro ao buscar habilitações: {err}", 'danger')

    form_data = request.form.to_dict()
    nome = form_data.get('nome')
    email = form_data.get('email')
    telefone = form_data.get('telefone')
    id_habilitacao = form_data.get('habilitacao')
    id_professor = form_data.get('id_professor')

    if request.method == 'POST':
        if not nome or not email or not telefone:
            flash("Preencha todos os campos obrigatórios!", 'warning')
            return render_template('cadastro-professor.html', habilitacoes=habilitacoes)

        try:
            with connection.cursor() as cursor:
                if id_professor:
                    # Atualiza os dados do professor
                    cursor.execute("UPDATE Professores SET nome=%s, email=%s, telefone=%s WHERE id_professor=%s;",
                                   (nome, email, telefone, id_professor))
                    connection.commit()

                    # Verifica se já existe uma habilitação associada
                    cursor.execute("SELECT id_habilitacao FROM Professores_X_Habilitacoes WHERE id_professor=%s;",
                                   (id_professor,))
                    habilitacao_existente = cursor.fetchone()

                    if id_habilitacao:
                        if habilitacao_existente:
                            # Atualiza a habilitação existente
                            cursor.execute("UPDATE Professores_X_Habilitacoes SET id_habilitacao=%s WHERE id_professor=%s;",
                                           (id_habilitacao, id_professor))
                        else:
                            # Insere uma nova habilitação se não existir
                            cursor.execute("INSERT INTO Professores_X_Habilitacoes (id_professor, id_habilitacao) VALUES (%s, %s);",
                                           (id_professor, id_habilitacao))
                    else:
                        if habilitacao_existente:
                            # Remove a habilitação se o usuário deixou em branco
                            cursor.execute("DELETE FROM Professores_X_Habilitacoes WHERE id_professor=%s;",
                                           (id_professor,))
                    connection.commit()
                    flash(f'Professor {nome} atualizado com sucesso!', 'success')

                else:
                    # Insere um novo professor
                    cursor.execute("INSERT INTO Professores (nome, email, telefone) VALUES (%s, %s, %s);",
                                   (nome, email, telefone))
                    connection.commit()
                    id_professor = cursor.lastrowid

                    if id_habilitacao:
                        cursor.execute("INSERT INTO Professores_X_Habilitacoes (id_professor, id_habilitacao) VALUES (%s, %s);",
                                       (id_professor, id_habilitacao))
                        connection.commit()

                    flash(f'Professor {nome} cadastrado com sucesso!', 'success')

        except Error as err:
            flash(f"Erro ao cadastrar/atualizar professor: {err}", 'danger')

        return redirect('/cadastro-professor')

    return render_template('cadastro-professor.html', habilitacoes=habilitacoes)

@app.route('/cadastro-disciplina', methods=['GET', 'POST'])
def cadastro_disciplina():
    """Renderiza a página de cadastro de disciplinas e processa inserções no banco."""
    habilitacoes = []
    connection = get_db_connection()

    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Habilitacoes")
                habilitacoes = cursor.fetchall()
        except Error as err:
            flash(f"Erro ao buscar habilitações: {err}", 'danger')

    form_data = request.form.to_dict()
    codigo = form_data.get('codigo')
    nome = form_data.get('nome')
    CH = form_data.get('CH')
    habilitacao_necessaria = form_data.get('habilitacao_necessaria')
    id_disciplina = form_data.get('id_disciplina')

    if request.method == 'POST':
        if not codigo or not nome or not CH or not habilitacao_necessaria:
            flash("Preencha todos os campos obrigatórios!", 'warning')
            return render_template('cadastro-disciplina.html', habilitacoes=habilitacoes)

        try:
            with connection.cursor() as cursor:
                if id_disciplina:
                    # Atualiza os dados da disciplina
                    cursor.execute("UPDATE Disciplinas SET codigo=%s, nome=%s, CH=%s, habilitacao_necessaria=%s WHERE id_disciplina=%s;",
                                   (codigo, nome, CH, habilitacao_necessaria, id_disciplina))
                    connection.commit()
                    flash(f'Disciplina {nome} atualizada com sucesso!', 'success')
                else:
                    # Insere uma nova disciplina
                    cursor.execute("INSERT INTO Disciplinas (codigo, nome, CH, habilitacao_necessaria) VALUES (%s, %s, %s, %s);",
                                   (codigo, nome, CH, habilitacao_necessaria))
                    connection.commit()
                    flash(f'Disciplina {nome} cadastrada com sucesso!', 'success')

        except Error as err:
            flash(f"Erro ao cadastrar/atualizar disciplina: {err}", 'danger')

        return redirect('/cadastro-disciplina')

    return render_template('cadastro-disciplina.html', habilitacoes=habilitacoes)

@app.route('/consulta-professor', methods=['GET'])
def consulta_professor():
    """Consulta todos os professores cadastrados."""
    professores = []
    connection = get_db_connection()

    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Professores")
                professores = cursor.fetchall()
        except Error as err:
            flash(f"Erro ao buscar professores: {err}", 'danger')

    return render_template('consulta-professor.html', professores=professores)


@app.route('/edicao-professor/<int:id_professor>', methods=['GET'])
def edicao_professor(id_professor):
    """Carrega os dados do professor e exibe o formulário de edição."""
    connection = get_db_connection()
    professor = None
    habilitacoes = []  # Adicionado para armazenar as habilitações

    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                # Buscar dados do professor
                cursor.execute("SELECT * FROM Professores WHERE id_professor = %s", (id_professor,))
                professor = cursor.fetchone()

                # Buscar lista de habilitações
                cursor.execute("SELECT * FROM Habilitacoes")
                habilitacoes = cursor.fetchall()

                # Buscar a habilitação associada ao professor
                cursor.execute("""
                    SELECT id_habilitacao 
                    FROM Professores_X_Habilitacoes 
                    WHERE id_professor = %s
                """, (id_professor,))
                resultado_habilitacao = cursor.fetchone()

                # Se houver uma habilitação associada, adiciona ao professor
                if resultado_habilitacao:
                    professor['id_habilitacao'] = resultado_habilitacao['id_habilitacao']

        except Error as err:
            flash(f"Erro ao buscar dados do professor: {err}", 'danger')

    return render_template('cadastro-professor.html', professor=professor, habilitacoes=habilitacoes)


@app.route('/exclusao-professor/<int:id_professor>', methods=['POST'])
def exclusao_professor(id_professor):
    """Exclui um professor do banco de dados."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM Professores WHERE id_professor = %s", (id_professor,))
                connection.commit()
                flash("Professor excluído com sucesso!", 'success')
        except Error as err:
            flash(f"Erro ao excluir professor: {err}", 'danger')
    return redirect('/consulta-professor')


