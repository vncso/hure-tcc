import functools
import db as db
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

bd_vagas = db.conn.hure.vagas
bd_candidatos = db.conn.hure.candidatos
bd_users = db.conn.hure.users

# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         nome = request.form.get('nome')
#         sobrenome = request.form.get('sobrenome')
#         datanasc = request.form.get('nasc')
#         email = request.form.get('email')
#         senha = request.form.get('senha')

#         bd = bd_users
#         error = None

#         #query = "INSERT INTO usuarios(nome, sobrenome, usuario, senha, datanasc, idcandidato) VALUES(?, ?, ?, ?, ?, 4)"

#         candidato = {
#             'nome': nome,
#             'sobrenome': sobrenome,
#             'email': email,
#             'senha': generate_password_hash(senha),
#             'datanasc': datanasc
#         }

#         bd.insert_one(candidato)

#         bd.update({'email': email},
#                   {'$set': {
#                       'experiencia': [
#                           {
#                               'empresa': 'Dentsply',
#                               'cargo': 'Aprendiz RH',
#                               'inicio': '02/02/2018',
#                               'fim': '20/12/2018',
#                               'atividades': 'Aprendiz, rotinas administrativas, recrutamento e seleção'
#                           },
#                           {
#                               'empresa': 'Baldin Bioenergia',
#                               'cargo': 'Analista de Suporte JR',
#                               'inicio': '20/08/2019',
#                               'fim': '01/02/2020',
#                               'atividades': 'Help Desk, suporte técnico, infraestrutura de T.I'
#                           },
#                           {
#                               'empresa': 'Baldin Bioenergia',
#                               'cargo': 'Analista de Sistemas JR/PL',
#                               'inicio': '01/02/2020',
#                               'fim': '',
#                               'atividades': 'Banco de dados, Totvs RM, desenvolvimento'
#                           }
#                       ]
#                   }
#                   }
#                   )

#         # bd.execute(query, (nome, sobrenome, email, generate_password_hash(senha), datanasc, ))

#         # hure.hure.db.conn.commit()

#         return redirect(url_for('index'))

#     return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        empresa = request.form.get('empresa')
        bd = bd_users
        # bd = hure.db.conn.cursor()
        error = None

        users = bd.find_one({'$and': [{'empresa': int(empresa)}, {'users.email': usuario}]}, {'users': 1})
        for user in users['users']:
            if user['email'] == usuario:
                verifica_senha = user['senha']
                if check_password_hash(verifica_senha, senha):
                    session.clear()
                    session['user_id'] = user['email']
                    session['empresa'] = empresa

                    if user['primeiro_acesso'] == 1:
                        session.clear()
                        session['user_id_temp'] = user['email']
                        session['empresa_temp'] = empresa
                        return redirect(url_for('auth.troca_senha'))

                    return redirect(url_for('rh.painel'))
                print(f'senha não bateu {verifica_senha} / {check_password_hash(verifica_senha, senha)}')
                flash('usuário ou senha incorretos', 'danger')
            else:
                print('erro de login')

    # query = 'SELECT * FROM usuarios WHERE usuario = ?'
    # bd.execute(query, (usuario,))
    # row = bd.fetchone()

    # if row is None:
    # error = 'Usuário incorreto'
    # elif not check_password_hash(row[3], senha):
    # error = 'Senha incorreta'

    # if error is None:
    #     session.clear()
    #     session['user_id'] = row[0]
    #     return redirect(url_for('auth.painel'))
    # flash(error)

    return render_template('auth/login.html')


def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('auth.login'))
        else:
            return func(*args, **kwargs)
    return secure_function


def login_required_troca_senha(func_troca_senha):
    @functools.wraps(func_troca_senha)
    def secure_function_troca_senha(*args, **kwargs):
        if "user_id_temp" not in session:
            return redirect(url_for('auth.login'))
        else:
            return func_troca_senha(*args, **kwargs)
    return secure_function_troca_senha

# @bp.route('/login/', methods=('GET', 'POST'))
# def login():
#     return render_template('hure/login.html')

@bp.route('/troca-senha', methods=['GET', 'POST'])
@login_required_troca_senha
def troca_senha():

    if request.method == 'POST':
        usuario = session['user_id_temp']
        empresa = session['empresa_temp']
        senha_atual = request.form.get('senha_atual')
        senha_nova = request.form.get('senha_nova')
        conf_senha_nova = request.form.get('conf_senha_nova')
        bd = bd_users
        
        users = bd.find_one({'$and': [{'empresa': int(empresa)}, {'users.email': usuario}]}, {'users': 1})

        print('DADOS DO BANCO DE DADOS:')
        print(users)

        for user in users['users']:
            print(user)
            if user['email'] == usuario and user['primeiro_acesso'] == 1:
                if check_password_hash(user['senha'], senha_atual):
                    if senha_nova == conf_senha_nova:
                        if senha_nova != senha_atual:
                            user['senha'] = generate_password_hash(senha_nova)
                            user['primeiro_acesso'] = 0

                            bd.update({'empresa': int(session['empresa_temp'])}, {
                                '$unset': {
                                    'users': ""
                                }
                            })

                            for user in users['users']:
                                bd.update({'empresa': int(session['empresa_temp'])}, {
                                    '$push': {
                                        'users': {
                                            'nome': user['nome'],
                                            'email': user['email'],
                                            'senha': user['senha'],
                                            'datanasc': user['datanasc'],
                                            'primeiro_acesso': user['primeiro_acesso'],
                                        }
                                    }
                                })
                            flash('Senha alterada com sucesso!', 'success')
                            return redirect(url_for('rh.painel'))
                        else:
                            flash('A nova senha não pode ser igual a senha antiga', 'danger')
                            return redirect(url_for('auth.troca_senha'))
                    else:
                        flash('A confirmação da senha falhou. Verifique se estão iguais.', 'danger')
                        return redirect(url_for('auth.troca_senha'))
                else:
                    flash('Senha antiga não está correta. Tente novamente', 'danger')
                    return redirect(url_for('auth.troca_senha'))
        else:
            flash('Senha não foi alterada', 'danger')
            return redirect(url_for('auth.troca_senha'))

    return render_template('auth/troca_senha.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
