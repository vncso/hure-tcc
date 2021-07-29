from flask import Flask, render_template, session, request, redirect, flash, url_for, current_app
from werkzeug.security import check_password_hash
import auth
import rh
import db as db
import misc
import candidatos
import os
import api.vagas as vagas
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth.bp)
    app.register_blueprint(rh.rh)
    app.register_blueprint(candidatos.person)
    app.register_blueprint(vagas.vagas)
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = 'static/imgs/'
    app.config['GOOGLEMAPS_KEY'] = os.environ.get('GOOGLE_MAPS_KEY')

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if request.form.get('empresa') != '':
                usuario = request.form.get('usuario')
                senha = request.form.get('senha')
                empresa = request.form.get('empresa')
                bd = db.conn.hure.users
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
                        return redirect(url_for('auth.login'))
                    else:
                        print('erro de login')

            else:
                senha = request.form.get('senha')
                usuario = request.form.get('usuario')
                vaga = request.form.get('idvaga')
                empresa = request.form.get('empresa')
                bd = db.conn.hure.candidatos
                # bd = hure.hure.db.conn.cursor()
                error = None

                user = bd.find_one({'email': usuario})
                print(user)
                if user == None:
                    redirect(url_for('person.register'))
                else:
                    verifica_senha = user['senha']
                    if check_password_hash(verifica_senha, senha):
                        session.clear()
                        session['cand_id'] = user['email']
                        if vaga is None:
                            return redirect(url_for('person.curriculo'))
                        else:
                            return redirect(url_for('vagas.vaga', empresa=empresa, idvaga=ObjectId(vaga)))
                    print(f'senha não bateu {verifica_senha} / {check_password_hash(verifica_senha, senha)}')
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

        return render_template('hure/index.html')

    @app.route('/servicos', methods=['GET', 'POST'])
    def servicos():
        if request.method == 'POST':
            if request.form.get('empresa') != '':
                usuario = request.form.get('usuario')
                senha = request.form.get('senha')
                empresa = request.form.get('empresa')
                bd = db.conn.hure.users
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
                        return redirect(url_for('auth.login'))
                    else:
                        print('erro de login')

            else:
                senha = request.form.get('senha')
                usuario = request.form.get('usuario')
                vaga = request.form.get('idvaga')
                empresa = request.form.get('empresa')
                bd = db.conn.hure.candidatos
                # bd = hure.hure.db.conn.cursor()
                error = None

                user = bd.find_one({'email': usuario})
                print(user)
                if user == None:
                    redirect(url_for('person.register'))
                else:
                    verifica_senha = user['senha']
                    if check_password_hash(verifica_senha, senha):
                        session.clear()
                        session['cand_id'] = user['email']
                        if vaga is None:
                            return redirect(url_for('person.curriculo'))
                        else:
                            return redirect(url_for('vagas.vaga', empresa=empresa, idvaga=ObjectId(vaga)))
                    print(f'senha não bateu {verifica_senha} / {check_password_hash(verifica_senha, senha)}')

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

        return render_template('hure/servicos.html')

    @app.route('/sobre', methods=['GET', 'POST'])
    def sobre():
        if request.method == 'POST':
            if request.form.get('empresa') != '':
                usuario = request.form.get('usuario')
                senha = request.form.get('senha')
                empresa = request.form.get('empresa')
                bd = db.conn.hure.users
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
                        return redirect(url_for('auth.login'))
                    else:
                        print('erro de login')

            else:
                senha = request.form.get('senha')
                usuario = request.form.get('usuario')
                vaga = request.form.get('idvaga')
                empresa = request.form.get('empresa')
                bd = db.conn.hure.candidatos
                # bd = hure.hure.db.conn.cursor()
                error = None

                user = bd.find_one({'email': usuario})
                print(user)
                if user == None:
                    redirect(url_for('person.register'))
                else:
                    verifica_senha = user['senha']
                    if check_password_hash(verifica_senha, senha):
                        session.clear()
                        session['cand_id'] = user['email']
                        if vaga is None:
                            return redirect(url_for('person.curriculo'))
                        else:
                            return redirect(url_for('vagas.vaga', empresa=empresa, idvaga=ObjectId(vaga)))
                    print(f'senha não bateu {verifica_senha} / {check_password_hash(verifica_senha, senha)}')

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

        return render_template('hure/sobre.html')

    return app
