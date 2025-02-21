from flask import Flask, jsonify, render_template, redirect, request, flash, url_for
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'matheusfce'

DB_CONFIG = {
    'host': 'localhost',
    'database': 'ProfEduDB',
    'user': 'root',
    'password': 'senha'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cadastro-professor', methods=['GET'])
def consulta_habilitacao():
    connect_db = None
    cursor = None
    habilitacoes = []

    try:
        connect_db = get_db_connection()
        cursor = connect_db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Habilitacoes")
        habilitacoes = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao buscar habilitações: {err}", 'danger')
    finally:
        if cursor:
            cursor.close()
        if connect_db and connect_db.is_connected():
            connect_db.close()

    return render_template('cadastro-professor.html', habilitacoes=habilitacoes)


@app.route('/insercao-professor', methods=['GET', 'POST'])
def insere_professor():
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    id_habilitacao = request.form.get('habilitacao')

    try:
        connect_db = get_db_connection()
        cursor = connect_db.cursor()
        cursor.execute("INSERT INTO Professores (nome, email, telefone) VALUES (%s, %s, %s);", (nome, email, telefone))
        connect_db.commit()
        id_professor = cursor.lastrowid

        if id_habilitacao and id_habilitacao.strip():
            try:
                cursor.execute("INSERT INTO Professores_X_Habilitacoes (id_professor, id_habilitacao) VALUES (%s, %s);",
                               (id_professor, id_habilitacao))
                connect_db.commit()
            except mysql.connector.Error as err:
                flash(f"Erro ao associar habilitação ao professor: {err}", 'danger')

        flash(f'Professor {nome} cadastrado com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f"Erro ao cadastrar professor: {err}", 'danger')

    finally:
        if cursor:
            cursor.close()
        if connect_db.is_connected():
            connect_db.close()

    return redirect('/cadastro-professor')

@app.route('/consulta-professor', methods=['GET'])
def consulta_professor():
    try:
        connect_db = get_db_connection()
        cursor = connect_db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Professores")
        professores = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao buscar professores: {err}", 'danger')
        professores = []
    finally:
        if cursor:
            cursor.close()
        if connect_db.is_connected():
            connect_db.close()

    return render_template('consulta-professor.html', professores=professores)

@app.route('/edicao-professor', methods=['GET'])
def edicao_professor():
    return render_template('menu.html')

@app.route('/exclusao-professor', methods=['GET'])
def exclusao_professor():
    return render_template('menu.html')

if __name__ == '__main__':
    app.run(debug=True)
