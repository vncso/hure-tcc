from flask import Flask, render_template, session, request, redirect, flash, url_for, current_app
from werkzeug.security import check_password_hash
import auth
import rh
import db as db
import candidatos
import api.vagas as vagas
from auth import fazer_login
import os
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
            usuario = request.form.get('usuario')
            senha = request.form.get('senha')
            empresa = request.form.get('empresa') if request.form.get('empresa') != '' else 0

            # chama a função para realizar o login
            login = fazer_login(int(empresa), usuario, senha)

            # Login para empresas (tipo = 0):
            if login['tipo'] == 0:
                if login['status'] == 1:
                    return redirect(url_for('auth.troca_senha'))
                elif login['status'] == 2:
                    return redirect(url_for('rh.painel'))
                else:
                    flash('Usuário ou senha incorretos. Tente novamente.')
                    return redirect(url_for('auth.login'))

            # Login para candidatos (tipo = 1):
            elif login['tipo'] == 1:
                if login['status'] == 0:
                    return redirect(url_for('person.register'))

                elif login['status'] == 1:
                    print('CHEGOU AQUI')
                    return redirect(url_for('person.curriculo'))
                else:
                    return redirect(url_for('vagas.vaga', empresa=login['empresa'], vaga=login['vaga']))
            else:
                return redirect(url_for('index'))

        return render_template('hure/index.html')

    @app.route('/servicos', methods=['GET', 'POST'])
    def servicos():
        if request.method == 'POST':
            usuario = request.form.get('usuario')
            senha = request.form.get('senha')
            empresa = request.form.get('empresa') if request.form.get('empresa') != '' else 0

            # chama a função para realizar o login
            login = fazer_login(int(empresa), usuario, senha)

            # Login para empresas (tipo = 0):
            if login['tipo'] == 0:
                if login['status'] == 1:
                    return redirect(url_for('auth.troca_senha'))
                elif login['status'] == 2:
                    return redirect(url_for('rh.painel'))
                else:
                    flash('Usuário ou senha incorretos. Tente novamente.')
                    return redirect(url_for('auth.login'))

            # Login para candidatos (tipo = 1):
            elif login['tipo'] == 1:
                if login['status'] == 0:
                    return redirect(url_for('person.register'))

                elif login['status'] == 1:
                    return redirect(url_for('person.curriculo'))
                else:
                    return redirect(url_for('vagas.vaga', empresa=login['empresa'], vaga=login['vaga']))
            else:
                return redirect(url_for('index'))

        return render_template('hure/servicos.html')

    @app.route('/sobre', methods=['GET', 'POST'])
    def sobre():
        if request.method == 'POST':
            usuario = request.form.get('usuario')
            senha = request.form.get('senha')
            empresa = request.form.get('empresa') if request.form.get('empresa') != '' else 0

            # chama a função para realizar o login
            login = fazer_login(int(empresa), usuario, senha)

            # Login para empresas (tipo = 0):
            if login['tipo'] == 0:
                if login['status'] == 1:
                    return redirect(url_for('auth.troca_senha'))
                elif login['status'] == 2:
                    return redirect(url_for('rh.painel'))
                else:
                    flash('Usuário ou senha incorretos. Tente novamente.')
                    return redirect(url_for('auth.login'))

            # Login para candidatos (tipo = 1):
            elif login['tipo'] == 1:
                if login['status'] == 0:
                    return redirect(url_for('person.register'))

                elif login['status'] == 1:
                    return redirect(url_for('person.curriculo'))
                else:
                    return redirect(url_for('vagas.vaga', empresa=login['empresa'], vaga=login['vaga']))
            else:
                return redirect(url_for('index'))

        return render_template('hure/sobre.html')

    return app