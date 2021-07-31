import functools
import db as db
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from datetime import datetime
import os
import re
import json
import datetime
import random
import string
import requests
from auth import login_required, fazer_login
from dotenv import load_dotenv

load_dotenv()

person = Blueprint('person', __name__, url_prefix='/candidato')

bd_vagas = db.conn.hure.vagas
bd_candidatos = db.conn.hure.candidatos
bd_users = db.conn.hure.users


def envia_email(destinatario, assunto, mensagem):
    """
        Função para envio de e-mails. Será usada no envio de confirmações, notificações e avisos sobre a conta
        e candidaturas feitas atraveś da plataforma.

        O serviço de e-mail utilizado é o 'MAILGUN'. Verificar no arquivo .env as variáveis de ambiente necessárias
        para que funcione sem erros

        Parametros:
            destinatario (str): quem vai receber o e-mail (usuário)
            assunto (str): título do e-mail
            mensagem (str): Mensagem enviada, em HTML.
    """
    return requests.post(
        'https://api.mailgun.net/v3/' + os.environ.get('MAILGUN_DOMAIN') + '/messages',
        auth=("api", os.environ.get('MAILGUN_API_KEY')),
        data={"from": "HuRe <info@hure.com.br>",
              "to": [destinatario],
              "subject": assunto,
              "html": mensagem})


def login_required_candidato(func):
    """
            função para limitar o acesso as áreas restritas da plataforma (áreas que somente usuários logados podem acessar)
            utilizamos as sessões criadas na função 'fazer login' para validar se o usuário está logado ou não.

            Essa função valida uma sessão diferente da função existente em auth.py

            se não estiver logado é redirecionado para a página de login.
        """
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "cand_id" not in session:
            return redirect(url_for('index'))
        else:
            return func(*args, **kwargs)

    return secure_function


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


@person.route('/register/', methods=['GET', 'POST'])
def register():
    """
        Página para cadastro do currículo do candidato.

    """
    if request.method == 'POST':
        # dados pessoais
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        genero = request.form.get('genero')
        datanasc = request.form.get('datanasc')
        email = request.form.get('email')
        senha = request.form.get('senha')
        conf_senha = request.form.get('conf_senha')

        # dados endereço e contatos
        cep = request.form.get('cep')
        rua = request.form.get('rua')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        tel = request.form.get('telefone')
        tel2 = request.form.get('telefone2')
        linkedin = request.form.get('linkedin')

        # dados da educação
        curso = request.form.get('curso')
        instituicao = request.form.get('instituicao')
        descri_curso = request.form.get('descri_curso')
        dataini_curso = request.form.get('dataini_curso')
        datafim_curso = request.form.get('datafim_curso')

        # dados para a experiência
        cargo = request.form.get('cargo')
        empresa = request.form.get('empresa')
        descri_xp = request.form.get('descri_xp')
        dataini_xp = request.form.get('dataini_xp')
        datafim_xp = request.form.get('datafim_xp')

        # Chave de ativação da conta (verificação por e-mail)
        chave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        bd = bd_candidatos
        error = None

        candidato = {
            'nome': nome,
            'sobrenome': sobrenome,
            'email': email,
            'senha': generate_password_hash(senha),
            'genero': genero,
            'datanasc': datanasc,
            'pcd': [],
            'endereco': {
                'cep': cep,
                'rua': rua,
                'numero': numero,
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado
            },
            'contato': {
                'tel1': tel,
                'tel2': tel2,
                'tel3': "",
                'facebook': "",
                'linkedin': linkedin,
                'site': "",
                'skype': ""
            },
            'cursos': [
                {
                    'nome': curso,
                    'instituicao': instituicao,
                    'inicio': dataini_curso,
                    'fim': datafim_curso,
                    'descricao': descri_curso
                }
            ] if (curso is None or curso == '') or (instituicao is None or instituicao == '') else [],
            'experiencias': [
                {
                    'cargo': cargo,
                    'empresa': empresa,
                    'inicio': dataini_xp,
                    'fim': datafim_xp,
                    'descricao': descri_xp
                }
            ] if (cargo is None or cargo == '') or (empresa is None or empresa == '') else [],
            'candidaturas': [],
            'anotacoes': [],
            'foto': '',
            'ativo': 0,
            'chave_ativa': chave

        }

        verifica = bd.find_one({'email': email})
        print(verifica)

        if verifica is None:
            verifica = {}

        print(verifica)

        # verifica se o candidato já está cadastrado
        if email in verifica.values():
            print('EMAIL JÁ CADASTRADO')
            flash('já existe uma conta com o e-mail informado, faça o login ou recupere a senha', 'info')
            return redirect(url_for('person.login'))
        else:
            print('USUÁRIO CRIADO COM SUCESSO')
            bd.insert_one(candidato)

            # envia o e-mail para confirmação da conta
            envia_email(email, 'HuRe - Verifique sua conta!',
                        '<div>'
                        '<link rel="preconnect" href="https://fonts.gstatic.com">'
                        '<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Righteous&display=swap" rel="stylesheet">'
                        '<link href="https://fonts.googleapis.com/css2?family=Jost:wght@500&display=swap" rel="stylesheet">'
                        '<div style="text-align: center">'
                        '<img src="https://www.hure.com.br/static/imgs/logo-header-mail.png">'
                        '</div>'
                        '</div>'
                        '<div>'
                        '<h5 style="font-family: \"Jost\";'
                        '           font-size: 1.2em;'
                        '           text-align: center;">'
                        'Seja bem vindo ao HuRe ;)'
                        '</h5>'
                        f'<p>Olá, {nome}!</p>'
                        '<p>Sua conta no HuRe foi criada com sucesso, agora só é preciso verificar a conta para garantir'
                        ' a sua segurança e acesso exclusivo a sua conta.'
                        '</p>'
                        '<p>Utilize o código abaixo para validar a sua conta. Finalizando essa etapa poderá completar o'
                        ' seu currículo e se candidatar a todas as vagas disponíveis em nossa plataforma.'
                        '</p>'
                        f'<h3>Seu código de verificação é: {chave}</h3>'
                        '<a href="https://www.hure.com.br/candidato/login/">clique aqui para ir direto ao HuRe</a>'
                        '</div>'
                        f'<p>Se você não é {nome}, ou não realizou nenhum cadastro em www.hure.com.br, por favor'
                        f'desconsidere este e-mail. Agradecemos a compreensão.'
                        '</p>'
                        )
        session.clear()
        session['email_verifica'] = email
        flash('currículo cadastrado com sucesso. Verifique seu e-mail para confirmar a conta!', 'success')
        return redirect(url_for('person.login_verifica'))

    return render_template('auth/register.html')


@person.route('/verifica-conta/', methods=['GET', 'POST'])
def login_verifica():
    """
        Verificação da conta pelo e-mail. O código é enviado para p e-mail informado ao criar o cadastro.

    """
    if request.method == 'POST':
        bd = bd_candidatos
        chave = request.form.get('chave')
        email = session['email_verifica']
        candidado = list(bd.find({'email': email, 'chave_ativa': chave}))
        print(candidado)
        print(email)
        print(chave)

        bd.update_one({'email': email, 'chave_ativa': chave},
                      {
                          '$set': {'ativo': 1}
                      }, False, True
                      )
        flash('Conta Verificada! Obrigado. Agora é só acessar ;)', 'success')
        return redirect(url_for('person.login'))

    return render_template('auth/verifica-candidato.html')


@person.route('/login/', methods=['GET', 'POST'])
def login():
    senha = request.form.get('senha')
    usuario = request.form.get('usuario')
    vaga = request.form.get('idvaga')
    empresa = request.form.get('empresa') if request.form.get('empresa') is not None else 0

    # chama a função para realizar o login
    login = fazer_login(int(empresa), usuario, senha, vaga)

    # Login para candidatos (tipo = 1):
    if login['tipo'] == 1:
        if login['status'] == 0:
            return redirect(url_for('person.register'))

        elif login['status'] == 1:
            return redirect(url_for('person.curriculo'))
        else:
            return redirect(url_for('vagas.vaga', empresa=login['empresa'], vaga=login['vaga']))
    else:
        return redirect(url_for('index'))

    return render_template('auth/login-candidato.html')


@person.route('/foto/<foto>/')
def foto(foto):
    bd = bd_candidatos
    img = bd.find({'foto.nome': foto}, {'foto.arquivo': 1})
    return img


@person.route('/curriculo/')
@login_required_candidato
def curriculo():
    bd = bd_candidatos
    user = list(bd.find({'email': session['cand_id']}).limit(1))
    user = user[0]

    return render_template('candidatos/curriculo.html', user=user, foto=foto)


@person.route('/atualiza-curriculo/', methods=['POST'])
@login_required_candidato
def atualiza_curriculo():
    bd = bd_candidatos
    if request.method == 'POST':
        print(request.form)
        # foto = request.files['foto']
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        datanasc = request.form.get('datanasc')
        cpf = request.form.get('cpf')
        genero = request.form.get('genero')
        etnia = request.form.get('etnia')
        pcd = request.form.get('pcd')
        pcd_detalhes = request.form.get('pcd_detalhes')
        pcd_outros = request.form.get('pcd_outros')
        cep = request.form.get('cep')
        rua = request.form.get('rua')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        tel1 = request.form.get('tel1')
        tel2 = request.form.get('tel2')
        tel3 = request.form.get('tel3')
        email = request.form.get('user_email')
        facebook = request.form.get('facebook')
        linkedin = request.form.get('linkedin')
        site = request.form.get('site')
        skype = request.form.get('skype')
        id_user = request.form.get('id_user')

        # foto.save(os.path.join('/static/imgs', secure_filename(foto.filename)))

        # print(foto)
        # print(foto.filename)

        bd.update({'_id': ObjectId(id_user)}, {
            '$set': {
                'foto': 'hure-logo.jpg',  # secure_filename(foto.filename),
                'nome': nome,
                'sobrenome': sobrenome,
                'email': email,
                'datanasc': datanasc,
                'cpf': cpf,
                'genero': genero,
                'etnia': etnia,
                'pcd': {
                    'sn': pcd,
                    'detalhes': pcd_detalhes,
                    'outros': pcd_outros
                },
                'endereco': {
                    'cep': cep,
                    'rua': rua,
                    'numero': numero,
                    'bairro': bairro,
                    'cidade': cidade,
                    'estado': estado
                },
                'contato': {
                    'tel1': tel1,
                    'tel2': tel2,
                    'tel3': tel3,
                    'facebook': facebook,
                    'linkedin': linkedin,
                    'site': site,
                    'skype': skype
                }

            }
        })

        return redirect(url_for('person.curriculo'))


@person.route('/cadastra-curriculo-bt/', methods=['POST'])
def cadastra_curriculo_bt():
    if request.method == 'POST':

        id_vaga = request.form.get('id_vaga')
        empresa_bt = request.form.get('empresa_bt')
        cidade_empresa = request.form.get('cidade_empresa')
        estado_empresa = request.form.get('estado_empresa')

        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        genero = request.form.get('genero')
        datanasc = request.form.get('datanasc')
        email = request.form.get('email')
        senha = request.form.get('senha')
        conf_senha = request.form.get('conf_senha')

        print(f'SENHA: {senha}')
        print(f'CONF. SENHA: {conf_senha}')

        cep = request.form.get('cep')
        rua = request.form.get('rua')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        tel = request.form.get('telefone')
        tel2 = request.form.get('telefone2')
        linkedin = request.form.get('linkedin')

        curso = request.form.get('curso')
        instituicao = request.form.get('instituicao')
        descri_curso = request.form.get('descri_curso')
        dataini_curso = request.form.get('dataini_curso')
        datafim_curso = request.form.get('datafim_curso')

        cargo = request.form.get('cargo')
        empresa = request.form.get('empresa')
        descri_xp = request.form.get('descri_xp')
        dataini_xp = request.form.get('dataini_xp')
        datafim_xp = request.form.get('datafim_xp')

        # Chave de ativação da conta (verificação por e-mail
        chave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        bd = bd_candidatos
        error = None

        candidato = {
            'nome': nome,
            'sobrenome': sobrenome,
            'email': email,
            'senha': generate_password_hash(senha),
            'genero': genero,
            'datanasc': datanasc,
            'pcd': [],
            'endereco': {
                'cep': cep,
                'rua': rua,
                'numero': numero,
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado
            },
            'contato': {
                'tel1': tel,
                'tel2': tel2,
                'tel3': "",
                'facebook': "",
                'linkedin': linkedin,
                'site': "",
                'skype': ""
            },
            'cursos': [
                {
                    'nome': curso,
                    'instituicao': instituicao,
                    'inicio': dataini_curso,
                    'fim': datafim_curso,
                    'descricao': descri_curso
                }
            ],
            'experiencias': [
                {
                    'cargo': cargo,
                    'empresa': empresa,
                    'inicio': dataini_xp,
                    'fim': datafim_xp,
                    'descricao': descri_xp
                }
            ],
            'candidaturas': [{
                'id': ObjectId(id_vaga),
                'cargo': 'Banco de Talentos',
                'empresa': empresa_bt,
                'cidade': cidade_empresa,
                'estado': estado_empresa,
                'status': 1,
                'respostas': [],
                'data': hoje
            }],
            'anotacoes': [],
            'foto': '',
            'ativo': 0,
            'chave_ativa': chave
        }

        verifica = bd.find_one({'email': email})
        print(verifica)

        if verifica is None:
            verifica = {}

        print(verifica)

        if email in verifica.values():
            print('EMAIL JÁ CADASTRADO')
            flash('já existe uma conta com o e-mail informado, faça o login ou recupere a senha', 'info')
            return redirect(url_for('person.login'))
        else:
            print('USUÁRIO CRIADO COM SUCESSO')
            bd.insert_one(candidato)

            envia_email(email, 'HuRe - Verifique sua conta!',
                        '<div>'
                        '<link rel="preconnect" href="https://fonts.gstatic.com">'
                        '<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Righteous&display=swap" rel="stylesheet">'
                        '<link href="https://fonts.googleapis.com/css2?family=Jost:wght@500&display=swap" rel="stylesheet">'
                        '<div style="text-align: center">'
                        '<img src="https://www.hure.com.br/static/imgs/logo-header-mail.png">'
                        '</div>'
                        '</div>'
                        '<div>'
                        '<h5 style="font-family: \"Jost\";'
                        '           font-size: 1.2em;'
                        '           text-align: center;">'
                        'Seja bem vindo ao HuRe ;)'
                        '</h5>'
                        f'<p>Olá, {nome}!</p>'
                        '<p>Sua conta no HuRe foi criada com sucesso, agora só é preciso verificar a conta para garantir'
                        ' a sua segurança e acesso exclusivo a sua conta.'
                        '</p>'
                        '<p>Utilize o código abaixo para validar a sua conta. Finalizando essa etapa poderá completar o'
                        ' seu currículo e se candidatar a todas as vagas disponíveis em nossa plataforma.'
                        '</p>'
                        f'<h3>Seu código de verificação é: {chave}</h3>'
                        '<a href="https://www.hure.com.br/candidato/login/">clique aqui para ir direto ao HuRe</a>'
                        '</div>'
                        f'<p>Se você não é {nome}, ou não realizou nenhum cadastro em www.hure.com.br, por favor'
                        f'desconsidere este e-mail. Agradecemos a compreensão.'
                        '</p>'
                        )
        session.clear()
        session['email_verifica'] = email
        flash('currículo cadastrado com sucesso. Verifique seu e-mail para confirmar a conta!', 'success')
        return redirect(url_for('person.login_verifica'))


@person.route('/login-bt/<int:empresa>/<bt_vaga>', methods=['GET', 'POST'])
def login_bt(empresa, bt_vaga):
    senha = request.form.get('senha')
    usuario = request.form.get('usuario')
    vaga = request.form.get('idvaga')
    nome_empresa = bd_users.find({'empresa': empresa}, {'nome': 1})
    bd = bd_candidatos
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
                verifica_cand = bd.find_one({'$and': [{'email': usuario}, {'candidaturas.id': ObjectId(bt_vaga)}]})

                if verifica_cand is None:
                    bd.update({'email': usuario}, {
                        '$push': {
                            'candidaturas': {
                                'id': ObjectId(bt_vaga),
                                'cargo': 'Banco de Talentos',
                                'empresa': empresa,
                                'nome_empresa': nome_empresa,
                                'cidade': 'Pirassununga',
                                'estado': 'SP',
                                'status': 1,
                                'respostas': []
                            }
                        }
                    })
                return redirect(url_for('person.curriculo'))
            else:
                return redirect(url_for('vagas.vaga', empresa=empresa, idvaga=ObjectId(vaga)))
        print(f'senha não bateu {verifica_senha} / {check_password_hash(verifica_senha, senha)}')

    return render_template('auth/login.html')


@person.route('/add-curso/', methods=['POST'])
@login_required_candidato
def add_curso():
    """
        Adiciona cursos ao curríulo.
    """
    bd = bd_candidatos
    if request.method == 'POST':
        curso = request.form.get('curso')
        instituicao = request.form.get('instituicao')
        inicio = request.form.get('datainicurso')
        fim = request.form.get('datafimcurso')
        descricao = request.form.get('descri_curso')
        candidato = request.form.get('id_user')

        bd.update({'_id': ObjectId(candidato)}, {
            '$push': {
                'cursos': {
                    'nome': curso,
                    'instituicao': instituicao,
                    'inicio': inicio,
                    'fim': fim,
                    'descricao': descricao
                }
            }
        })

        return redirect(url_for('person.curriculo'))


@person.route('/add-experiencia/', methods=['POST'])
@login_required_candidato
def add_experiencia():
    """
        Adiciona experiências ao curríulo.
    """
    bd = bd_candidatos
    if request.method == 'POST':
        cargo = request.form.get('cargo')
        empresa = request.form.get('empresa')
        inicio = request.form.get('datainixp')
        fim = request.form.get('datafimxp')
        descricao = request.form.get('descri_cargo')
        candidato = request.form.get('id_user')

        bd.update({"_id": ObjectId(candidato)}, {
            "$push": {
                "experiencias": {
                    'cargo': cargo,
                    'empresa': empresa,
                    'inicio': inicio,
                    'fim': fim,
                    'descricao': descricao
                }
            }
        })

        return redirect(url_for('person.curriculo'))


@person.route('candidaturas/')
@login_required_candidato
def candidaturas():
    """
        Retorna todas as candidaturas do candidato logado.
    """
    bd = bd_candidatos

    vagas = list(bd.find({'email': session['cand_id']}, {'candidaturas': 1}))

    for vg in vagas:
        print(vg)
        for vaga in vg['candidaturas']:
            print(vaga['cargo'])

    bd = bd_candidatos
    user = list(bd.find({'email': session['cand_id']}).limit(1))
    user = user[0]

    return render_template('candidatos/candidaturas.html', vagas=vagas, user=user)


@person.route('/verifica-cand-email/', methods=['POST'])
def verifica_cand_email():
    """
        Verifica em tempo real se o e-mail informado já está cadastrado.
    """
    bd = bd_candidatos
    query = request.form.get('email')
    # busca = re.compile(f'.*{query}*.', re.IGNORECASE)

    print(f'EMAIL:{query}')

    candidatos = list(bd.find({'email': query}, {'email': 1}))

    return JSONEncoder().encode(candidatos[0])
