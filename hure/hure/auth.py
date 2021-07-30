import functools
import db as db
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')

bd_vagas = db.conn.hure.vagas
bd_candidatos = db.conn.hure.candidatos
bd_users = db.conn.hure.users


def fazer_login(empresa, usuario, senha, vaga=0):
    """
        Função para realizar o login no app.

        Parametros:
            empresa (int): codigo da empresa [opcional]
            usuario (str): email do usuário [obrigatório]
            senha (str): senha do usuário [obrigatório]
            vaga (ObjectId): identificador de uma vaga para redirecionamento [opcional]

        Retorno da função:
            Essa função cria a sessão do usuário caso os dados informados sejam válidos
            senão retorna uma mensagem de erro para o usuário (flash).

            se for empresa o retorno será um dicionário com os dados (tipo, status, usuário e empresa)
                tipo (int): 0 que representa o login para empresas
                status (int): pode ter os valores 0, 1 ou 2 que representam as situações abaixo:
                    0: Login inválido
                    1: primeiro acesso (alterar senha)
                    2: login OK
                usuário (str): receberá o email do usuário para registrar a sessão
                empresa (int): receberá o codigo da empresa para registrar a sessão
    """

    # verifica se o login é para empresa ou candidato
    if empresa != 0:
        usuario = usuario
        senha = senha
        empresa = empresa
        bd = db.conn.hure.users
        error = None

        users = bd.find_one({'$and': [{'empresa': int(empresa)}, {'users.email': usuario}]}, {'users': 1})
        for user in users['users']:
            print(user)
            if user['email'] == usuario:
                verifica_senha = user['senha']
                if check_password_hash(verifica_senha, senha):
                    print('Senha OK')
                    session.clear()
                    session['user_id'] = user['email']
                    session['empresa'] = empresa

                    # em caso de primeiro acesso para empresas, a senha deve ser alterada
                    if user['primeiro_acesso'] == 1:
                        retorno_login = {'tipo': 0, 'status': 1, 'usuario': user['email'], 'empresa': empresa}
                        session.clear()
                        session['user_id_temp'] = retorno_login['usuario']
                        session['empresa_temp'] = retorno_login['empresa']
                        return retorno_login

                    retorno_login = {'tipo': 0, 'status': 2, 'usuario': user['email'], 'empresa': empresa}
                    session.clear()
                    session['user_id'] = retorno_login['usuario']
                    session['empresa'] = retorno_login['empresa']
                    print('chegou aqui')
                    return retorno_login

                retorno_login = {'tipo': 0, 'status': 0, 'usuario': user['email'], 'empresa': empresa}
                flash('usuário ou senha incorretos', 'danger')
                return retorno_login

            else:
                print('erro de login')

    # se no login não for informado o código da empresa, é feito o login como o candidato
    else:
        """
            O login para o candidato segue o mesmo padrão do login para a empresa, porém sem a necessidade de
            preencher o primeiro parametro obrigatoriamente. Sendo necessário apenas para redirecionar para 
            a página de uma vaga.

            O retorno da função no caso do candidato é o seguinte dicionário:
                (tipo, status, usuário, empresa, vaga)
                    tipo (int): 1 que irá representar o login para candidatos
                    status (int): pode ter os valores 0, 1 ou 2 que representam as situações abaixo:
                        0: não cadastrado
                        1: login OK (currículo)
                        2: login OK (redirecionar para vaga)
                    usuário (str): receberá o email do usuário para registrar a sessão
                    empresa (int): receberá o codigo da empresa para redirecionar para a vaga
                    vaga (ObjectId): receberá o ID da vaga para redirecionamento.
        """
        senha = senha
        usuario = usuario
        # caso o login seja feito pela página de uma vaga para redirecionamento:
        vaga = vaga
        empresa = empresa
        bd = db.conn.hure.candidatos
        error = None

        user = bd.find_one({'email': usuario})
        print(user)
        # se o candidato não está cadastrado, redireciona para a tela de cadastro
        if user is None:
            retorno_login = {'tipo': 1, 'status': 0, 'usuario': None, 'empresa': 0, 'vaga': None}
            return retorno_login
        else:
            verifica_senha = user['senha']
            if check_password_hash(verifica_senha, senha):
                if vaga is None or vaga == 0:
                    retorno_login = {'tipo': 1, 'status': 1, 'usuario': user['email'], 'empresa': 0, 'vaga': None}
                    session.clear()
                    session['cand_id'] = retorno_login['usuario']
                    return retorno_login
                else:
                    retorno_login = {'tipo': 1, 'status': 2, 'usuario': user['email'], 'empresa': empresa, 'vaga': ObjectId(vaga)}
                    session.clear()
                    session['cand_id'] = retorno_login['usuario']
                    return retorno_login
            print(f'senha não bateu {verifica_senha} / {check_password_hash(verifica_senha, senha)}')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
        página de login para as empresas. Essa página possui um formulários com os campos 'codigo da empresa',
        'usuario' e 'senha'. O login é feito enviando os parametros para a função 'fazer_login'.

        Parametros:
            cod. empresa (int): codigo da empresa
            usuario (str): e-mail do usuário que irá acessar
            senha (str): senha do usuário que irá acessar
    """
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        empresa = int(request.form.get('empresa'))

        login = fazer_login(empresa, usuario, senha)

        if login['status'] == 1:
            session.clear()
            session['user_id_temp'] = login['usuario']
            session['empresa_temp'] = login['empresa']
            return redirect(url_for('auth.troca_senha'))

        elif login['status'] == 2:
            session.clear()
            session['user_id'] = login['usuario']
            session['empresa'] = login['empresa']
            return redirect(url_for('rh.painel'))

        else:
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


def login_required(func):
    """
        função para limitar o acesso as áreas restritas da plataforma (áreas que somente usuários logados podem acessar)
        utilizamos as sessões criadas na função 'fazer login' para validar se o usuário está logado ou não.

        se não estiver logado é redirecionado para a página de login.
    """
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('auth.login'))
        else:
            return func(*args, **kwargs)
    return secure_function


def login_required_troca_senha(func_troca_senha):
    """
        função para validar a sessão de troca de senha no primeiro acesso do usuário.
        a sessão salva é diferente da sessão responsável pelo login, por isso esta nova função é necessária.
    """
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
    """
        Página para trocar de senha no primeiro acesso a plataforma. Essa tela é exibida somente para as empresas.
        a troca de senha é necessária para garantir a segurança do usuário.
    """
    if request.method == 'POST':
        usuario = session['user_id_temp']
        empresa = session['empresa_temp']
        senha_atual = request.form.get('senha_atual')
        senha_nova = request.form.get('senha_nova')
        conf_senha_nova = request.form.get('conf_senha_nova')
        bd = bd_users
        
        users = bd.find_one({'$and': [{'empresa': int(empresa)}, {'users.email': usuario}]}, {'users': 1})

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
