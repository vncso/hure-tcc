import pymongo
import db as db
import misc as misc
from candidatos import envia_email
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
import datetime
from datetime import date
import json
import requests
import re
import os
from operator import itemgetter
from auth import login_required
from bson.objectid import ObjectId
from flask_googlemaps import get_address, get_coordinates
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('HERE_MAPS_KEY')

rh = Blueprint('rh', __name__, url_prefix='/rh')

bd_vagas = db.conn.hure.vagas
bd_candidatos = db.conn.hure.candidatos
bd_users = db.conn.hure.users


@rh.route('/edita-vaga/<idvaga>', methods=['GET', 'POST'])
@login_required
def edita_vaga(idvaga):
    """
        RF-8: Editar vagas de emprego publicadas

        Página para edição de uma vaga publicada na plataforma. Essa página deve trazer todas as informações de uma
        vaga publicada anteriormente que ainda não esteja com o status de "fechada (3)".

    """
    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    bd = bd_vagas
    empresa = session['empresa']
    buscavaga = list(bd.find({'$and': [{'_id': ObjectId(idvaga)}, {'empresa': int(empresa)}]}))
    vaga = buscavaga[0]

    if request.method == 'POST':
        cargo = request.form.get('cargo')
        descricao = request.form.get('descricao')
        empresa = int(session['empresa'])
        requisitos = request.form.get('requisitos').split(";")
        beneficios = request.form.get('beneficios').split(";")
        salario = request.form.get('salario')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        pcd = request.form.get('pcd')
        tipo = request.form.get('tipo')
        prazo = request.form.get('prazo')

        # PERGUNTAS E QUESTIONÁRIO
        pergunta_0 = request.form.get('pergunta_0')
        tipo_0 = int(request.form.get('tipo_0')) if pergunta_0 is not None else 0
        obrigatoria_0 = request.form.get('obrigatoria_0') if pergunta_0 is not None else 0
        respostas_0 = request.form.get('respostas_0').split(';') if pergunta_0 is not None else 0
        sequencia_0 = int(request.form.get('sequencia_0')) if pergunta_0 is not None else 0

        pergunta_1 = request.form.get('pergunta_1')
        tipo_1 = int(request.form.get('tipo_1')) if pergunta_1 is not None else 0
        obrigatoria_1 = request.form.get('obrigatoria_1') if pergunta_1 is not None else 0
        respostas_1 = request.form.get('respostas_1').split(';') if pergunta_1 is not None else 0
        sequencia_1 = int(request.form.get('sequencia_1')) if pergunta_1 is not None else 0

        pergunta_2 = request.form.get('pergunta_2')
        tipo_2 = int(request.form.get('tipo_2')) if pergunta_2 is not None else 0
        obrigatoria_2 = request.form.get('obrigatoria_2') if pergunta_2 is not None else 0
        respostas_2 = request.form.get('respostas_2').split(';') if pergunta_2 is not None else 0
        sequencia_2 = int(request.form.get('sequencia_2')) if pergunta_2 is not None else 0

        pergunta_3 = request.form.get('pergunta_3')
        tipo_3 = int(request.form.get('tipo_3')) if pergunta_3 is not None else 0
        obrigatoria_3 = request.form.get('obrigatoria_3') if pergunta_3 is not None else 0
        respostas_3 = request.form.get('respostas_3').split(';') if pergunta_3 is not None else 0
        sequencia_3 = int(request.form.get('sequencia_3')) if pergunta_3 is not None else 0

        pergunta_4 = request.form.get('pergunta_4')
        tipo_4 = int(request.form.get('tipo_4')) if pergunta_4 is not None else 0
        obrigatoria_4 = request.form.get('obrigatoria_4') if pergunta_4 is not None else 0
        respostas_4 = request.form.get('respostas_4').split(';') if pergunta_4 is not None else 0
        sequencia_4 = int(request.form.get('sequencia_4')) if pergunta_4 is not None else 0

        pergunta_5 = request.form.get('pergunta_5')
        tipo_5 = int(request.form.get('tipo_5')) if pergunta_5 is not None else 0
        obrigatoria_5 = request.form.get('obrigatoria_5') if pergunta_5 is not None else 0
        respostas_5 = request.form.get('respostas_5').split(';') if pergunta_5 is not None else 0
        sequencia_5 = int(request.form.get('sequencia_5')) if pergunta_5 is not None else 0

        pergunta_6 = request.form.get('pergunta_6')
        tipo_6 = int(request.form.get('tipo_6')) if pergunta_6 is not None else 0
        obrigatoria_6 = request.form.get('obrigatoria_6') if pergunta_6 is not None else 0
        respostas_6 = request.form.get('respostas_6').split(';') if pergunta_6 is not None else 0
        sequencia_6 = int(request.form.get('sequencia_6')) if pergunta_6 is not None else 0

        pergunta_7 = request.form.get('pergunta_7')
        tipo_7 = int(request.form.get('tipo_7')) if pergunta_7 is not None else 0
        obrigatoria_7 = request.form.get('obrigatoria_7') if pergunta_7 is not None else 0
        respostas_7 = request.form.get('respostas_7').split(';') if pergunta_7 is not None else 0
        sequencia_7 = int(request.form.get('sequencia_7')) if pergunta_7 is not None else 0

        perguntas = [
            {
                'tipo': tipo_0,
                'obrigatoria': int(obrigatoria_0),
                'pergunta': pergunta_0,
                'respostas': respostas_0,
                'pgt': sequencia_0,
                'ativa': 1 if pergunta_0 is not None else 0
            },
            {
                'tipo': tipo_1,
                'obrigatoria': int(obrigatoria_1),
                'pergunta': pergunta_1,
                'respostas': respostas_1,
                'pgt': sequencia_1,
                'ativa': 1 if pergunta_1 is not None else 0
            },
            {
                'tipo': tipo_2,
                'obrigatoria': int(obrigatoria_2),
                'pergunta': pergunta_2,
                'respostas': respostas_2,
                'pgt': sequencia_2,
                'ativa': 1 if pergunta_2 is not None else 0
            },
            {
                'tipo': tipo_3,
                'obrigatoria': int(obrigatoria_3),
                'pergunta': pergunta_3,
                'respostas': respostas_3,
                'pgt': sequencia_3,
                'ativa': 1 if pergunta_3 is not None else 0
            },
            {
                'tipo': tipo_4,
                'obrigatoria': int(obrigatoria_4),
                'pergunta': pergunta_4,
                'respostas': respostas_4,
                'pgt': sequencia_4,
                'ativa': 1 if pergunta_4 is not None else 0
            },
            {
                'tipo': tipo_5,
                'obrigatoria': int(obrigatoria_5),
                'pergunta': pergunta_5,
                'respostas': respostas_5,
                'pgt': sequencia_5,
                'ativa': 1 if pergunta_5 is not None else 0
            },
            {
                'tipo': tipo_6,
                'obrigatoria': int(obrigatoria_6),
                'pergunta': pergunta_6,
                'respostas': respostas_6,
                'pgt': sequencia_6,
                'ativa': 1 if pergunta_6 is not None else 0
            },
            {
                'tipo': tipo_7,
                'obrigatoria': int(obrigatoria_7),
                'pergunta': pergunta_7,
                'respostas': respostas_7,
                'pgt': sequencia_7,
                'ativa': 1 if pergunta_7 is not None else 0
            },
        ]
        contador = request.form.get('contador_pgt')
        publicada = request.form.get('publicada')
        palavras_chave = request.form.get('palavras_chave')

        """
            Verificação de palavras que podem ser interpretadas de maneira errônea ou que são ofensivas no conteúdo
            da vaga. Se for encontrada uma palavra que seja ofensiva o sistema informa e pede a confirmação do usuário
            sobre se deseja ou não realmente continuar.
        """
        ignora_palavra = int(request.form.get('ignora_palavra'))
        palavra_ignorada = request.form.get('palavra_ignorada')
        ignoradas_form = request.form.get('ignoradas') if request.form.get('ignoradas') is not None else 'hure'
        palavra_ignoradas_form = ignoradas_form.split(';')
        hoje = datetime.datetime.now()
        bd = bd_vagas
        ignoradas = [x for x in palavra_ignoradas_form]
        ignoradas.append(palavra_ignorada)
        filtro = [re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', x.lower()) for x in misc.palavras_ofensivas]
        palavras_descricao = descricao.split(' ')
        palavras_descricao_check = [re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', x.lower()) for x in
                                    palavras_descricao]

        for palavra in palavras_descricao_check:
            if re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', palavra) in filtro and palavra not in ignoradas:
                flash(f'a palavra "{palavra}" encontrada na descrição da vaga pode ser considerada ofensiva ou '
                      f'pode ser interpretada da maneira incorreta. Se deseja prosseguir clique em "Continuar".',
                      'danger')
                return render_template('rh/abre-vaga.html', cargo=cargo, descricao=descricao, cidade=cidade,
                                       prazo=prazo, estado=estado, requisitos=requisitos, beneficios=beneficios,
                                       user=user, salario=salario, ignoradas=ignoradas, palavra=palavra,
                                       perguntas=perguntas,
                                       contador=contador, inicial=0)
        else:
            bd.update({'_id': ObjectId(idvaga)}, {
                '$set': {
                    'cargo': cargo,
                    'descricao': descricao,
                    'empresa': empresa,
                    'requisitos': requisitos,
                    'beneficios': beneficios,
                    'salario': salario,
                    'localizacao': {
                        'cidade': cidade,
                        'estado': estado
                    },
                    'pcd': pcd,
                    'qtd_perguntas': int(contador),
                    'perguntas': perguntas,
                    'tipo': tipo,
                    'prazo': prazo,
                    'publicacao': hoje,
                    'publicada': int(publicada)
                }
            })

        flash('Vaga editada com sucesso!', 'success')
        return redirect(url_for('rh.painel'))

    return render_template('rh/edita-vaga.html', vaga=vaga,
                                                  user=user,
                                                inicial=1)


@rh.route('/abre-vaga/', methods=['GET', 'POST'])
@login_required
def abre_vaga():
    """"
        RF-2: Cadastro e publicação de vagas de emprego

        página para abrir uma vaga pela plataforma. Possibilita a abertura de vagas, adição de perguntas ao questionario
        e a publicação da vaga criada.


    """
    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    if request.method == 'POST':
        cargo = request.form.get('cargo')
        descricao = request.form.get('descricao')
        empresa = int(session['empresa'])
        requisitos = request.form.get('requisitos').split(";")
        beneficios = request.form.get('beneficios').split(";")
        salario = request.form.get('salario')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        pcd = request.form.get('pcd')
        tipo = request.form.get('tipo')
        prazo = request.form.get('prazo')

        # PERGUNTAS E QUESTIONÁRIO
        """
            RF-5: Adicionar perguntas a uma vaga de emprego (questionário)
        """
        pergunta_0 = request.form.get('pergunta_0')
        tipo_0 = int(request.form.get('tipo_0')) if pergunta_0 is not None else 0
        obrigatoria_0 = request.form.get('obrigatoria_0') if pergunta_0 is not None else 0
        respostas_0 = request.form.get('respostas_0').split(';') if pergunta_0 is not None else 0
        sequencia_0 = int(request.form.get('sequencia_0')) if pergunta_0 is not None else 0

        pergunta_1 = request.form.get('pergunta_1')
        tipo_1 = int(request.form.get('tipo_1')) if pergunta_1 is not None else 0
        obrigatoria_1 = request.form.get('obrigatoria_1') if pergunta_1 is not None else 0
        respostas_1 = request.form.get('respostas_1').split(';') if pergunta_1 is not None else 0
        sequencia_1 = int(request.form.get('sequencia_1')) if pergunta_1 is not None else 0

        pergunta_2 = request.form.get('pergunta_2')
        tipo_2 = int(request.form.get('tipo_2')) if pergunta_2 is not None else 0
        obrigatoria_2 = request.form.get('obrigatoria_2') if pergunta_2 is not None else 0
        respostas_2 = request.form.get('respostas_2').split(';') if pergunta_2 is not None else 0
        sequencia_2 = int(request.form.get('sequencia_2')) if pergunta_2 is not None else 0

        pergunta_3 = request.form.get('pergunta_3')
        tipo_3 = int(request.form.get('tipo_3')) if pergunta_3 is not None else 0
        obrigatoria_3 = request.form.get('obrigatoria_3') if pergunta_3 is not None else 0
        respostas_3 = request.form.get('respostas_3').split(';') if pergunta_3 is not None else 0
        sequencia_3 = int(request.form.get('sequencia_3')) if pergunta_3 is not None else 0

        pergunta_4 = request.form.get('pergunta_4')
        tipo_4 = int(request.form.get('tipo_4')) if pergunta_4 is not None else 0
        obrigatoria_4 = request.form.get('obrigatoria_4') if pergunta_4 is not None else 0
        respostas_4 = request.form.get('respostas_4').split(';') if pergunta_4 is not None else 0
        sequencia_4 = int(request.form.get('sequencia_4')) if pergunta_4 is not None else 0

        pergunta_5 = request.form.get('pergunta_5')
        tipo_5 = int(request.form.get('tipo_5')) if pergunta_5 is not None else 0
        obrigatoria_5 = request.form.get('obrigatoria_5') if pergunta_5 is not None else 0
        respostas_5 = request.form.get('respostas_5').split(';') if pergunta_5 is not None else 0
        sequencia_5 = int(request.form.get('sequencia_5')) if pergunta_5 is not None else 0

        pergunta_6 = request.form.get('pergunta_6')
        tipo_6 = int(request.form.get('tipo_6')) if pergunta_6 is not None else 0
        obrigatoria_6 = request.form.get('obrigatoria_6') if pergunta_6 is not None else 0
        respostas_6 = request.form.get('respostas_6').split(';') if pergunta_6 is not None else 0
        sequencia_6 = int(request.form.get('sequencia_6')) if pergunta_6 is not None else 0

        pergunta_7 = request.form.get('pergunta_7')
        tipo_7 = int(request.form.get('tipo_7')) if pergunta_7 is not None else 0
        obrigatoria_7 = request.form.get('obrigatoria_7') if pergunta_7 is not None else 0
        respostas_7 = request.form.get('respostas_7').split(';') if pergunta_7 is not None else 0
        sequencia_7 = int(request.form.get('sequencia_7')) if pergunta_7 is not None else 0

        perguntas = [
                    {
                        'tipo': tipo_0,
                        'obrigatoria': obrigatoria_0,
                        'pergunta': pergunta_0,
                        'respostas': respostas_0,
                        'pgt': sequencia_0,
                        'ativa': 1 if pergunta_0 is not None else 0
                    },
                    {
                        'tipo': tipo_1,
                        'obrigatoria': obrigatoria_1,
                        'pergunta': pergunta_1,
                        'respostas': respostas_1,
                        'pgt': sequencia_1,
                        'ativa': 1 if pergunta_1 is not None else 0
                    },
                    {
                        'tipo': tipo_2,
                        'obrigatoria': obrigatoria_2,
                        'pergunta': pergunta_2,
                        'respostas': respostas_2,
                        'pgt': sequencia_2,
                        'ativa': 1 if pergunta_2 is not None else 0
                    },
                    {
                        'tipo': tipo_3,
                        'obrigatoria': obrigatoria_3,
                        'pergunta': pergunta_3,
                        'respostas': respostas_3,
                        'pgt': sequencia_3,
                        'ativa': 1 if pergunta_3 is not None else 0
                    },
                    {
                        'tipo': tipo_4,
                        'obrigatoria': obrigatoria_4,
                        'pergunta': pergunta_4,
                        'respostas': respostas_4,
                        'pgt': sequencia_4,
                        'ativa': 1 if pergunta_4 is not None else 0
                    },
                    {
                        'tipo': tipo_5,
                        'obrigatoria': obrigatoria_5,
                        'pergunta': pergunta_5,
                        'respostas': respostas_5,
                        'pgt': sequencia_5,
                        'ativa': 1 if pergunta_5 is not None else 0
                    },
                    {
                        'tipo': tipo_6,
                        'obrigatoria': obrigatoria_6,
                        'pergunta': pergunta_6,
                        'respostas': respostas_6,
                        'pgt': sequencia_6,
                        'ativa': 1 if pergunta_6 is not None else 0
                    },
                    {
                        'tipo': tipo_7,
                        'obrigatoria': obrigatoria_7,
                        'pergunta': pergunta_7,
                        'respostas': respostas_7,
                        'pgt': sequencia_7,
                        'ativa': 1 if pergunta_7 is not None else 0
                    },
                ]
        contador = request.form.get('contador_pgt')  # quantidade de perguntas adicionadas a vaga

        publicada = request.form.get('publicada')
        palavras_chave = request.form.get('palavras_chave')

        """
            Verificação de palavras que podem ser interpretadas de maneira errônea ou que são ofensivas no conteúdo
            da vaga. Se for encontrada uma palavra que seja ofensiva o sistema informa e pede a confirmação do usuário
            sobre se deseja ou não realmente continuar.
        """
        ignora_palavra = int(request.form.get('ignora_palavra'))
        palavra_ignorada = request.form.get('palavra_ignorada')
        ignoradas_form = request.form.get('ignoradas') if request.form.get('ignoradas') is not None else 'hure'
        palavra_ignoradas_form = ignoradas_form.split(';')
        hoje = datetime.datetime.now()
        bd = bd_vagas
        ignoradas = [x for x in palavra_ignoradas_form]
        ignoradas.append(palavra_ignorada)
        filtro = [re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', x.lower()) for x in misc.palavras_ofensivas]
        palavras_descricao = descricao.split(' ')
        palavras_descricao_check = [re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', x.lower()) for x in palavras_descricao]

        for palavra in palavras_descricao_check:
            if re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', palavra) in filtro and palavra not in ignoradas:
                flash(f'a palavra "{palavra}" encontrada na descrição da vaga pode ser considerada ofensiva ou '
                      f'pode ser interpretada da maneira incorreta. Se deseja prosseguir clique em "Continuar".', 'danger')
                return render_template('rh/abre-vaga.html', cargo=cargo, descricao=descricao, cidade=cidade,
                                       prazo=prazo, estado=estado, requisitos=requisitos, beneficios=beneficios,
                                       user=user, salario=salario, ignoradas=ignoradas, palavra=palavra, perguntas=perguntas,
                                       contador=contador, inicial=0)
        else:
            error = None
            vaga = {
                'cargo': cargo,
                'descricao': descricao,
                'empresa': empresa,
                'requisitos': requisitos,
                'beneficios': beneficios,
                'salario': salario,
                'localizacao': {
                    'cidade': cidade,
                    'estado': estado
                },
                'pcd': pcd,
                'tipo': tipo,
                'prazo': prazo,
                'publicacao': hoje,
                'qtd_perguntas': int(contador),
                'perguntas': perguntas,
                'publicada': int(publicada),
                'palavras': palavras_chave
            }

            bd.insert_one(vaga)

            flash('Vaga Anunciada com sucesso!', 'success')
            return redirect(url_for('rh.painel'))

    return render_template('rh/abre-vaga.html', user=user, inicial=1)


@rh.route('processo/<idvaga>')
@login_required
def processo(idvaga):
    """
        RF-4: Consulta de candidaturas nas vagas publicadas

        Página para verificação do andamento das candidaturas em uma vaga. Aqui a empresa consegue ver quem se candidatou
        para uma vaga publicada.
    """
    bd = bd_candidatos
    candidatos = list(bd.find({'$and': [{'candidaturas.id': ObjectId(idvaga)},
                                        {'candidaturas.empresa': int(session['empresa'])}]}))

    cands = []
    print(candidatos)
    for candidato in candidatos:
        for candidatura in candidato['candidaturas']:
            if candidatura['id'] == ObjectId(idvaga) and candidatura['status'] == 0:
                cands.append(candidato)
                
    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    bd = bd_vagas
    vaga = list(bd.find({'$and': [{'_id': ObjectId(idvaga)}, {'empresa': int(session['empresa'])}]}))

    return render_template('rh/processo.html', user=user, candidatos=cands, vaga=vaga, idvaga=ObjectId(idvaga))


@rh.route('/painel')
@login_required
def painel():

    empresa = session['empresa']
    print(empresa)

    bd = bd_vagas
    # vagas abertas pela empresa
    vagas = list(bd.find({'empresa': int(empresa)}).limit(6).sort('publicacao'))

    # QTD. vagas abertas no mês pela empresa
    hoje = date.today()
    mes = hoje.month
    vagas_mes = len(list(bd.find({'$and': [{'empresa': int(empresa)},
                                           {'$expr': {
                                            '$eq': [{ '$month': '$publicacao'}, mes]
                                            }}
                                           ]})))
    mes_anterior = hoje.month - 1
    vagas_mes_anterior = len(list(bd.find({'$and': [{'empresa': int(empresa)},
                                           {'$expr': {
                                               '$eq': [{'$month': '$publicacao'}, mes_anterior]
                                           }}
                                           ]})))

    if vagas_mes_anterior == 0:
        vagas_mes_anterior = 1

    bd = bd_candidatos
    candidatos = len(list(bd.find({'candidaturas.empresa': int(session['empresa'])}, {'_id': 1})))




    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr
    return render_template('auth/painel.html', **locals())


@rh.route('banco-de-talentos/')
@login_required
def banco_de_talentos():
    """
        RF-3: Consulta de candidatos no banco de talentos

        Página que permite a busca de candidatos no Banco de Talentos. Por padrão são exibidos os cadastros mais
        recentes, mas a busca dinâmica pode ser realizada no campo de busca disponível.
        O campo faz uma requisição via AJAX à função "get_candidatos(empresa)" que retorna os candidatos que atendem
        aos critérios de busca.

    """
    bd = bd_candidatos
    candidatos = list(bd.find({'candidaturas.empresa': int(session['empresa'])}).limit(48))

    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    return render_template('rh/banco-de-talentos.html', user=user, candidatos=candidatos)


@rh.route('curriculo/<candidato>')
@login_required
def curriculo(candidato):
    bd = bd_candidatos
    candidato = bd.find_one({'_id': ObjectId(candidato)})
    
    # ENDEREÇO CANDIDATO
    URL = "https://geocode.search.hereapi.com/v1/geocode"
    location = candidato['endereco']['rua']+', '+candidato['endereco']['numero']+', '+candidato['endereco']['cidade']+'/'+candidato['endereco']['estado']
    api_key = API_KEY  # Acquire from developer.here.com
    PARAMS = {'apikey': api_key, 'q': location}

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()

    latitude = data['items'][0]['position']['lat']
    longitude = data['items'][0]['position']['lng']
    endereco_url = location

    print(longitude, latitude)
    if len(candidato['anotacoes']) <= 0:
        candidato['anotacoes'] = []
    anotacoes = [anotacao for anotacao in candidato['anotacoes'] if anotacao['empresa'] == int(session['empresa'])]
    anotacoes = len(anotacoes)
    print(anotacoes)
    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']

    print(user)
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    bd = bd_users
    empresa = list(bd.find({'empresa': int(session['empresa'])}))
    empresa = empresa[0]
    print(empresa)

    mapa = empresa['mapa']

    mapa = mapa.replace('{{latitude}}', str(latitude))
    mapa = mapa.replace('{{longitude}}', str(longitude))
    mapa = mapa.replace('{{endereco_url}}', str(endereco_url))

    nasc = datetime.datetime.strptime(user['datanasc'], '%Y-%m-%d')
    hoje = datetime.datetime.now()
    idade = abs((hoje - nasc).days) // 365

    bd = bd_vagas
    vagas = list(bd.find({'empresa': int(session['empresa'])}))

    return render_template('rh/curriculo.html', empresa=int(session['empresa']), candidato=candidato, vagas=vagas, 
                           user=user, latitude=latitude, longitude=longitude, endereco_url=endereco_url,
                           idade=idade, anotacoes=anotacoes, mapa=mapa)


# @rh.route('/add_questionario_vaga/', methods=['GET', 'POST'])
# @login_required
# def add_questionario_vaga():
#     if request.method == 'POST':
#         vaga = request.form.get('vaga_id')
#         tipo_pergunta = int(request.form.get('tipo_pergunta'))
#         pergunta_obrigatoria = int(request.form.get('pergunta_obrigatoria'))
#         pergunta = request.form.get('pergunta')
#         opcoes_pergunta = request.form.get('opcoes_pergunta').split(';')
#         bd = bd_vagas
#         pgt = list(bd.find({'_id': ObjectId(vaga)}, {'perguntas.pgt': 1}))
#         qtd = 0
#         print('PGT:')
#         print(pgt)
#         if 'perguntas' in pgt[0]:
#             for p in pgt[0]['perguntas']:
#                 for q in p.values():
#                     qtd = q + 1
#         else:
#             qtd = 0
#
#         bd.update({'_id': ObjectId(vaga)}, {
#             '$push': {
#                 'perguntas': {
#                     'tipo': tipo_pergunta,
#                     'obrigatoria': pergunta_obrigatoria,
#                     'pergunta': pergunta,
#                     'opcoes': opcoes_pergunta,
#                     'pgt': qtd,
#                     'ativa': 1
#                 }
#             }
#         })
#
#         return redirect(url_for('rh.edita_vaga', idvaga=ObjectId(vaga)))


# @rh.route('/del-questionario-vaga/', methods=['GET', 'POST'])
# @login_required
# def del_questionario_vaga():
#     if request.method == 'POST':
#         vaga = request.form.get('id_vaga')
#         n = int(request.form.get('numero'))
#         bd = bd_vagas
#         pgt = list(bd.find({'_id': ObjectId(vaga)}, {'perguntas': 1}))
#         print('VAGAS:')
#         print(pgt[0]['perguntas'][0])
#         print(n)
#         remover = next((i for i, item in enumerate(pgt[0]['perguntas']) if item['pgt'] == n), None)
#         print(remover)
#         pgt[0]['perguntas'].pop(remover)
#
#         bd.update({'_id': ObjectId(vaga)}, {
#             '$unset': {
#                 'perguntas': ""
#             }
#         })
#
#         for pergunta in pgt[0]['perguntas']:
#             bd.update({'_id': ObjectId(vaga)}, {
#                 '$push': {
#                     'perguntas': {
#                         'tipo': pergunta['tipo'],
#                         'obrigatoria': pergunta['obrigatoria'],
#                         'pergunta': pergunta['pergunta'],
#                         'opcoes': pergunta['opcoes'],
#                         'pgt': pergunta['pgt'],
#                         'ativa': 1
#                     }
#                 }
#             })
#
#         bd.update({'_id': ObjectId(vaga)}, {
#             '$set': {
#                 'perguntas': {
#                     pgt[0]['perguntas']
#                 }
#             }
#         })
#
#         return redirect(url_for('rh.edita_vaga', idvaga=ObjectId(vaga)))


@rh.route('/add_opt_vaga/', methods=['GET', 'POST'])
@login_required
def add_opt_vaga():
    if request.method == 'POST':
        vaga = request.form.get('id_vaga')
        publicada = int(request.form.get('publicada'))
        palavras = request.form.get('palavras_chave').split(';')
        bd = bd_vagas
        bd.update({'_id': ObjectId(vaga)}, {
            '$set': {
                'publicada': publicada,
                'palavras': palavras
            }
        })
        return redirect(url_for('rh.edita_vaga', idvaga=ObjectId(vaga)))


@rh.route('deleta-vaga/<idvaga>')
@login_required
def deleta_vaga(idvaga):

    vaga = ObjectId(idvaga)
    empresa = int(session['empresa'])
    bd = bd_vagas

    bd.delete_one({'$and': [{'_id': vaga}, {'empresa': empresa}]})

    flash('Vaga deletada com sucesso!', 'success')
    return redirect(url_for('rh.painel'))


@rh.route('add-anotacao-curriculo', methods=['POST'])
@login_required
def add_anotacao_curriculo():
    """
        RF-6: Adicionar anotações em um currículo no banco de talentos

        Função para adicionar anotações em um currículo que está no Banco de talentos.
    """
    if request.method == 'POST':
        candidato = request.form.get('candidato')
        empresa = int(session['empresa'])
        tipo = request.form.get('tipo')
        anotacao = request.form.get('anotacao')
        bd = bd_candidatos
        notes = list(bd.find({'_id': ObjectId(candidato)}, {'anotacoes': 1}))

        remover = next((i for i, item in enumerate(notes[0]['anotacoes']) if item['_id'] == 0),
                       None)
        print(remover)
        if remover is not None:
            notes[0]['anotacoes'].pop(remover)

            bd.update({'_id': ObjectId(candidato)}, {
                '$unset': {
                    'anotacoes': ""
                }
            })

        bd.update({'_id': ObjectId(candidato)}, {
            '$push': {
                'anotacoes': {
                    '_id': ObjectId(),
                    'tipo': tipo,
                    'empresa': empresa,
                    'anotacao': anotacao,
                }
            }
        })

        return redirect(url_for('rh.curriculo', candidato=candidato))

    
@rh.route('/del-anotacao-curriculo/', methods=['POST'])
@login_required
def del_anotacao_curriculo():
    """
            RF-6: Adicionar anotações em um currículo no banco de talentos

            Função para remover anotações em um currículo que está no Banco de talentos.
        """
    if request.method == 'POST':
        candidato = request.form.get('candidato')
        id_anotacao = request.form.get('id_anotacao')
        bd = bd_candidatos
        notes = list(bd.find({'_id': ObjectId(candidato)}, {'anotacoes': 1}))
        print('VAGAS:')
        print(notes[0]['anotacoes'])
        remover = next((i for i, item in enumerate(notes[0]['anotacoes']) if item['_id'] == ObjectId(id_anotacao)), None)

        print(remover)

        notes[0]['anotacoes'].pop(remover)

        bd.update({'_id': ObjectId(candidato)}, {
            '$unset': {
                'anotacoes': ""
            }
        })

        if len(notes[0]['anotacoes']) > 0:
            for anotacao in notes[0]['anotacoes']:
                print("INSERINDO")
                print(anotacao)
                bd.update({'_id': ObjectId(candidato)}, {
                    '$push': {
                        'anotacoes': {
                            '_id': anotacao['_id'],
                            'tipo': anotacao['tipo'],
                            'empresa': int(anotacao['empresa']),
                            'anotacao': anotacao['anotacao']
                        }
                    }
                })
        else:
            bd.update({'_id': ObjectId(candidato)}, {
                '$push': {
                    'anotacoes': {
                        '_id': 0,
                        'tipo': 0,
                        'empresa': 0,
                        'anotacao': '0'
                    }
                }
            })

        return redirect(url_for('rh.curriculo', candidato=ObjectId(candidato)))
    

@rh.route('/get-candidatos/<int:empresa>', methods=['GET', 'POST'])
@login_required
def get_candidatos(empresa):

    bd = bd_candidatos
    query = request.form.get('busca')
    busca = re.compile(f'.*{query}*.', re.IGNORECASE)

    print(f'BUSCA: {busca}')
    
    if busca == '' or busca is None:

        candidados = list(bd.find({'candidaturas.empresa': empresa}).limit(48).sort('nome'))

        return render_template('rh/candidatos.html', candidatos=candidados)

    candidatos = list(bd.find({'$and': [{'candidaturas.empresa': empresa},
                                        {'$or': [
                                            {'nome': busca},
                                            {'sobrenome': busca},
                                            {'endereco.cidade': busca},
                                            {'cursos.nome': busca},
                                            {'cursos.descricao': busca},
                                            {'experiencias.cargo': busca},
                                            {'experiencias.descricao': busca}
                                        ]}]}))

    return render_template('rh/candidatos.html', candidatos=candidatos)


@rh.route('/get-candidatos-proc/<int:empresa>/<idvaga>', methods=['GET', 'POST'])
@login_required
def get_candidatos_proc(empresa, idvaga):

    bd = bd_candidatos
    query = request.form.get('busca_cand')
    vaga = request.form.get('vaga_id')
    resultado_busca = []
    busca = re.compile(f'.*{query}*.', re.IGNORECASE)
    
    print(f'BUSCA: {busca}')

    if busca == '' or busca is None:

        candidados = list(bd.find({'$and': [{'candidaturas.empresa': empresa}, 
                                            {'candidaturas.id': ObjectId(vaga)},
                                            {'candidaturas.status': 0}]}).limit(48).sort('nome'))

        return render_template('rh/candidatos-proc.html', candidatos=candidados)

    candidatos = list(bd.find({'$or': [
                                    {'$and': [
                                        {'nome': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]},
                                    {'$and': [
                                        {'sobrenome': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]},
                                    {'$and': [
                                        {'endereco.cidade': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]},
                                    {'$and': [
                                        {'cursos.nome': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]},
                                    {'$and': [
                                        {'cursos.descricao': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]},
                                    {'$and': [
                                        {'experiencias.cargo': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]},
                                    {'$and': [
                                        {'experiencias.descricao': busca},
                                        {'candidaturas.empresa': empresa}, {'candidaturas.id': ObjectId(vaga)},
                                        {'candidaturas.status': 0}
                                    ]}
                                ]}
                            ))

    """
        Aqui utilizamos a lista retornada pela consulta no BD para filtrar os candidatos que se candidataram para
        a vaga a qual o processo está sendo acompanhado. Dessa forma garantimos que só aparecerão nos resultados
        de busca os candidatos que aplicaram para a vaga.
    """

    for candidato in candidatos:
        for candidatura in candidato['candidaturas']:
            if candidatura['id'] == ObjectId(vaga) and candidatura['status'] == 0:
                resultado_busca.append(candidato)

    return render_template('rh/candidatos-proc.html', candidatos=resultado_busca)


@rh.route('/aprova-candidato', methods=['POST'])
@login_required
def aprova_candidato():
    """
       RF-7: Mover um candidato do Banco de Talentos para uma vaga aberta
       RF-9: Aprovar ou reprovar candidatos

       Aprova candidatos para uma determinada vaga em aberto.
    """
    if request.method == 'POST':
        id_candidato = request.form.get('candidato')
        id_vaga = request.form.get('vaga')
        nome_candidato = request.form.get('nome_candidato')
        origem = request.form.get('origem')
        data = request.form.get('data')

        bd = bd_vagas
        vaga = list(bd.find({'_id': ObjectId(id_vaga)}))

        bd = bd_candidatos
        candidato = list(bd.find({'_id': ObjectId(id_candidato)}))

        candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                            {'candidaturas.id': ObjectId(id_vaga)}]}))

        verifica_cand = bd.find_one({'$and': [{'_id': ObjectId(id_candidato)}, {'candidaturas.id': ObjectId(id_vaga)}]})

        if origem == 'processo':
            if verifica_cand is None:
                vaga = bd_vagas
                vg = vaga.find_one({'_id': ObjectId(id_vaga)})
                bd.update({'_id': ObjectId(id_candidato)}, {
                    '$push': {
                        'candidaturas': {
                            'id': ObjectId(id_vaga),
                            'cargo': vg['cargo'],
                            'empresa': vg['empresa'],
                            'cidade': vg['localizacao']['cidade'],
                            'estado': vg['localizacao']['estado'],
                            'status': 1,
                            'respostas': candidatura[0]['respostas'] if candidatura[0]['respostas'] else [],
                            'data': data
                        }
                    }
                })

            remover = next((i for i, item in enumerate(candidatura[0]['candidaturas']) if item['id'] == ObjectId(id_vaga)), None)

            candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                                 {'candidaturas.id': ObjectId(id_vaga)}]}))

            candidatura[0]['candidaturas'][remover]['status'] = 1

            cargo_vaga = candidatura[0]['candidaturas'][remover]['cargo']

            bd.update({'_id': ObjectId(id_candidato)}, {
                '$unset': {
                    'candidaturas': ""
                }
            })

            for candidatura in candidatura[0]['candidaturas']:
                bd.update({'_id': ObjectId(id_candidato)}, {
                    '$push': {
                        'candidaturas': {
                            'id': candidatura['id'],
                            'cargo': candidatura['cargo'],
                            'empresa': candidatura['empresa'],
                            'cidade': candidatura['cidade'],
                            'estado': candidatura['estado'],
                            'status': candidatura['status'],
                            'respostas': candidatura['respostas'],
                            'etapas': [{
                                'curriculo': 1,
                                'entrevista': 0,
                                'entrevista_tecnica': 0,
                                'entrevista_gestor': 0
                            }],
                            'etapas_admissao': [{
                                'psicologico': 0,
                                'documentos': 0,
                                'aso': 0,
                                'integracao': 0
                            }]
                        }
                    }
                })
            envia_email(candidato[0]['email'], f'Seu Currículo foi aprovado para a vaga {vaga[0]["cargo"]}',
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
                        f'Atualização sobre a sua candidatura para a vaga {vaga[0]["cargo"]}'
                        '</h5>'
                        f'<p>Olá, {candidato[0]["nome"]}!</p>'
                        '<p>Temos uma boa notícia. Seu currículo foi aprovado na primeira etapa do processo seletivo para'
                        f' o cargo {vaga[0]["cargo"]}. Acesse sua conta para acompanhar as próximas etapas.'
                        '</p>'
                        '<a href="https://www.hure.com.br/candidato/login/">clique aqui para ir direto ao HuRe</a>'
                        '</div>'
                        )
            flash(f'O currículo de {nome_candidato} foi aprovado!', 'success')
            return redirect(url_for('rh.processo', idvaga=id_vaga))

        elif origem == 'curriculo':
            if verifica_cand is None:
                vaga = bd_vagas
                vg = vaga.find_one({'_id': ObjectId(id_vaga)})
                bd.update({'_id': ObjectId(id_candidato)}, {
                    '$push': {
                        'candidaturas': {
                            'id': ObjectId(id_vaga),
                            'cargo': vg['cargo'],
                            'empresa': vg['empresa'],
                            'cidade': vg['localizacao']['cidade'],
                            'estado': vg['localizacao']['estado'],
                            'status': 1,
                            'respostas': [],
                            'data': data
                        }
                    }
                })

            candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                                 {'candidaturas.id': ObjectId(id_vaga)}]}))
            remover = next(
                (i for i, item in enumerate(candidatura[0]['candidaturas']) if item['id'] == ObjectId(id_vaga)), None)

            candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                                 {'candidaturas.id': ObjectId(id_vaga)}]}))

            candidatura[0]['candidaturas'][remover]['status'] = 1

            bd.update({'_id': ObjectId(id_candidato)}, {
                '$unset': {
                    'candidaturas': ""
                }
            })

            for candidatura in candidatura[0]['candidaturas']:
                bd.update({'_id': ObjectId(id_candidato)}, {
                    '$push': {
                        'candidaturas': {
                            'id': candidatura['id'],
                            'cargo': candidatura['cargo'],
                            'empresa': candidatura['empresa'],
                            'cidade': candidatura['cidade'],
                            'estado': candidatura['estado'],
                            'status': candidatura['status'],
                            'respostas': [],
                            'etapas': [{
                                'curriculo': 1,
                                'entrevista': 0,
                                'entrevista_tecnica': 0,
                                'entrevista_gestor': 0
                            }],
                            'etapas_admissao': [{
                                'psicologico': 0,
                                'documentos': 0,
                                'aso': 0,
                                'integracao': 0
                            }]
                        }
                    }
                })
            if verifica_cand is None:
                flash(f"{nome_candidato} foi incluído no processo para a vaga {vaga[0]['cargo']}", "success")
                return redirect(url_for('rh.curriculo', candidato=id_candidato))
            else:
                flash(f"{nome_candidato} já está no processo para a vaga {vaga[0]['cargo']}", "info")
                return redirect(url_for('rh.curriculo', candidato=id_candidato))


@rh.route('/reprova-candidato', methods=['POST'])
@login_required
def reprova_candidato():
    """
        RF-9: Aprovar ou reprovar candidatos

        Reprova candidatos em uma determinada vaga em aberto.
    """
    if request.method == 'POST':
        id_candidato = request.form.get('candidato')
        id_vaga = request.form.get('vaga')
        nome_candidato = request.form.get('nome_candidato')
        origem = request.form.get('origem')
        cargo_vaga = request.form.get('cargo')
        bd = bd_candidatos

        candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                                 {'candidaturas.id': ObjectId(id_vaga)}]}))

        remover = next((i for i, item in enumerate(candidatura[0]['candidaturas']) if item['id'] == ObjectId(id_vaga)), None)

        candidatura[0]['candidaturas'][remover]['status'] = 2

        bd.update({'_id': ObjectId(id_candidato)}, {
            '$unset': {
                'candidaturas': ""
            }
        })

        for candidatura in candidatura[0]['candidaturas']:
            bd.update({'_id': ObjectId(id_candidato)}, {
                '$push': {
                    'candidaturas': {
                        'id': candidatura['id'],
                        'cargo': candidatura['cargo'],
                        'empresa': candidatura['empresa'],
                        'cidade': candidatura['cidade'],
                        'estado': candidatura['estado'],
                        'status': candidatura['status'],
                        'respostas': candidatura['respostas'],
                        'etapas': [{
                            'curriculo': 2,
                            'entrevista': 0,
                            'entrevista_tecnica': 0,
                            'entrevista_gestor': 0
                        }]
                    }
                }
            })

        if origem == 'processo':
            flash(f'O currículo de {nome_candidato} foi reprovado.', 'info')
            return redirect(url_for('rh.processo', idvaga=id_vaga))
        elif origem == 'triagem':
            flash(f"{nome_candidato} foi reprovado no processo para a vaga {cargo_vaga}", "info")
            return redirect(url_for('rh.triagem'))


@rh.route('/triagem')
@login_required
def triagem():

    empresa = int(session['empresa'])
    bd = bd_vagas
    vagas = list(bd.find({'empresa': empresa}))

    bd = bd_candidatos
    candidatos = list(bd.find({'candidaturas.empresa': empresa}))

    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    return render_template('rh/triagem.html', vagas=vagas, candidatos=candidatos, user=user)


@rh.route('/admite-candidato', methods=['POST'])
@login_required
def admite_candidato():

    if request.method == 'POST':
        id_candidato = request.form.get('candidato')
        id_vaga = request.form.get('vaga')
        nome_candidato = request.form.get('nome_candidato')
        cargo = request.form.get('cargo')
        bd = bd_candidatos

        candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                             {'candidaturas.id': ObjectId(id_vaga)}]}))

        verifica_cand = bd.find_one({'$and': [{'_id': ObjectId(id_candidato)}, {'candidaturas.id': ObjectId(id_vaga)}]})

        if verifica_cand is None:
            vaga = bd_vagas
            vg = vaga.find_one({'_id': ObjectId(id_vaga)})
            bd.update({'_id': ObjectId(id_candidato)}, {
                '$push': {
                    'candidaturas': {
                        'id': ObjectId(id_vaga),
                        'cargo': vg['cargo'],
                        'empresa': vg['empresa'],
                        'cidade': vg['localizacao']['cidade'],
                        'estado': vg['localizacao']['estado'],
                        'status': 1,
                        'respostas': []
                    }
                }
            })

        remover = next((i for i, item in enumerate(candidatura[0]['candidaturas']) if item['id'] == ObjectId(id_vaga)),
                       None)

        candidatura[0]['candidaturas'][remover]['status'] = 3

        bd.update({'_id': ObjectId(id_candidato)}, {
            '$unset': {
                'candidaturas': ""
            }
        })

        for candidatura in candidatura[0]['candidaturas']:
            bd.update({'_id': ObjectId(id_candidato)}, {
                '$push': {
                    'candidaturas': {
                        'id': candidatura['id'],
                        'cargo': candidatura['cargo'],
                        'empresa': candidatura['empresa'],
                        'cidade': candidatura['cidade'],
                        'estado': candidatura['estado'],
                        'status': candidatura['status'],
                        'respostas': candidatura['respostas'],
                        'etapas': candidatura['etapas'],
                        'etapas_admissao': [{
                            'psicologico': 0,
                            'documentos': 0,
                            'aso': 0,
                            'integracao': 0
                        }]
                    }
                }
            })

        flash(f'{nome_candidato} foi encaminhado para a admissão!', 'success')
        return redirect(url_for('rh.triagem'))


@rh.route('/admissao/')
@login_required
def admissao():

    empresa = int(session['empresa'])
    bd = bd_vagas
    vagas = list(bd.find({'empresa': empresa}))

    bd = bd_candidatos
    candidatos = list(bd.find({'candidaturas.empresa': empresa}))

    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    return render_template('rh/admissao.html', vagas=vagas, candidatos=candidatos, user=user)


@rh.route('/fecha-vaga/<idvaga>', methods=['GET','POST'])
@login_required
def fecha_vaga(idvaga):
    empresa = int(session['empresa'])
    bd = bd_vagas

    cargo = bd.find_one({'_id': ObjectId(idvaga)}, {'cargo': 1})

    bd.update_one({'$and': [{'empresa': empresa}, {'_id': ObjectId(idvaga)}]}, {
        '$set': {
            'publicada': 3,
        }
    })

    flash(f'vaga para {cargo["cargo"]} fechada com sucesso! Visualize em "Histórico de vagas"')
    return redirect(url_for('rh.painel'))


@rh.route('/historico-vagas/')
@login_required
def historico_vagas():

    empresa = session['empresa']
    print(empresa)

    bd = bd_vagas
    vagas = list(bd.find({'empresa': int(empresa)}).sort('publicacao', -1))

    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr
    return render_template('rh/historico_vagas.html', **locals())


@rh.route('/aprova-reprova-etapa', methods=['POST'])
@login_required
def aprova_reprova_etapa():

    empresa = int(session['empresa'])
    id_candidato = request.form.get('candidato')
    id_vaga = request.form.get('vaga')
    etapa = request.form.get('etapa')
    aprova_reprova = request.form.get('aprova_reprova')
    bd = bd_candidatos
    nome_candidato = request.form.get('nome_candidato')

    candidatura = list(bd.find({'$and': [{'_id': ObjectId(id_candidato)},
                                         {'candidaturas.id': ObjectId(id_vaga)}]}))

    verifica_cand = bd.find_one({'$and': [{'_id': ObjectId(id_candidato)}, {'candidaturas.id': ObjectId(id_vaga)}]})

    if verifica_cand is None:
        vaga = bd_vagas
        vg = vaga.find_one({'_id': ObjectId(id_vaga)})
        bd.update({'_id': ObjectId(id_candidato)}, {
            '$push': {
                'candidaturas': {
                    'id': ObjectId(id_vaga),
                    'cargo': vg['cargo'],
                    'empresa': vg['empresa'],
                    'cidade': vg['localizacao']['cidade'],
                    'estado': vg['localizacao']['estado'],
                    'status': 1,
                    'respostas': []
                }
            }
        })

    remover = next((i for i, item in enumerate(candidatura[0]['candidaturas']) if item['id'] == ObjectId(id_vaga)),
                   None)

    print('ENTREVISTA:')
    print(candidatura[0]['candidaturas'][remover]['etapas'][0]['entrevista'])

    entrevista = candidatura[0]['candidaturas'][remover]['etapas'][0]['entrevista']
    entrevista_tecnica = candidatura[0]['candidaturas'][remover]['etapas'][0]['entrevista_tecnica']
    entrevista_gestor = candidatura[0]['candidaturas'][remover]['etapas'][0]['entrevista_gestor']

    psicologico = candidatura[0]['candidaturas'][remover]['etapas_admissao'][0]['psicologico']
    documentos = candidatura[0]['candidaturas'][remover]['etapas_admissao'][0]['documentos']
    aso = candidatura[0]['candidaturas'][remover]['etapas_admissao'][0]['aso']
    integracao = candidatura[0]['candidaturas'][remover]['etapas_admissao'][0]['integracao']

    cargo_vaga = candidatura[0]['candidaturas'][remover]['cargo']

    bd.update({'_id': ObjectId(id_candidato)}, {
        '$unset': {
            'candidaturas': ""
        }
    })

    if aprova_reprova == 'aprova':
        for candidatura in candidatura[0]['candidaturas']:
            bd.update({'_id': ObjectId(id_candidato)}, {
                '$push': {
                    'candidaturas': {
                        'id': candidatura['id'],
                        'cargo': candidatura['cargo'],
                        'empresa': candidatura['empresa'],
                        'cidade': candidatura['cidade'],
                        'estado': candidatura['estado'],
                        'status': candidatura['status'],
                        'respostas': candidatura['respostas'],
                        'etapas': [{
                            'curriculo': 1,
                            'entrevista': 1 if etapa == 'entrevista' else entrevista,
                            'entrevista_tecnica': 1 if etapa == 'entrevista_tecnica' else entrevista_tecnica,
                            'entrevista_gestor': 1 if etapa == 'entrevista_gestor' else entrevista_gestor
                        }],
                        'etapas_admissao': [{
                            'psicologico': 1 if etapa == 'psicologico' else psicologico,
                            'documentos': 1 if etapa == 'documentos' else documentos,
                            'aso': 1 if etapa == 'aso' else aso,
                            'integracao': 1 if etapa == 'integracao' else integracao
                        }]
                    }
                }
            })

        flash(f'{nome_candidato} aprovado na etapa {etapa} para a vaga {cargo_vaga}', 'success')
        if etapa == 'psicologico' or etapa == 'documentos' or etapa == 'aso' or etapa == 'integracao':
            return redirect(url_for('rh.admissao'))
        else:
            return redirect(url_for('rh.triagem'))
    else:
        for candidatura in candidatura[0]['candidaturas']:
            bd.update({'_id': ObjectId(id_candidato)}, {
                '$push': {
                    'candidaturas': {
                        'id': candidatura['id'],
                        'cargo': candidatura['cargo'],
                        'empresa': candidatura['empresa'],
                        'cidade': candidatura['cidade'],
                        'estado': candidatura['estado'],
                        'status': candidatura['status'],
                        'respostas': candidatura['respostas'],
                        'etapas': [{
                            'curriculo': 1,
                            'entrevista': 2 if etapa == 'entrevista' else entrevista,
                            'entrevista_tecnica': 2 if etapa == 'entrevista_tecnica' else entrevista_tecnica,
                            'entrevista_gestor': 2 if etapa == 'entrevista_gestor' else entrevista_gestor
                        }],
                        'etapas_admissao': [{
                            'psicologico': 2 if etapa == 'psicologico' else psicologico,
                            'documentos': 2 if etapa == 'documentos' else documentos,
                            'aso': 2 if etapa == 'aso' else aso,
                            'integracao': 2 if etapa == 'integracao' else integracao
                        }]
                    }
                }
            })

        flash(f'{nome_candidato} reprovado na etapa {etapa} para a vaga {cargo_vaga}', 'info')
        return redirect(url_for('rh.triagem'))


@rh.route('/empresa', methods=['GET', 'POST'])
@login_required
def empresa():
    bd = bd_users
    user = list(bd.find({'$and': [{'empresa': int(session['empresa'])}, {'users.email': session['user_id']}]}).limit(1))
    user = user[0]['users']
    for usr in user:
        if session['user_id'] in usr.values():
            user = usr

    if request.method == 'POST':
        nome_fantasia = request.form.get('nome_fantasia')
        cnpj = request.form.get('cnpj')
        cidade = request.form.get('cidade')
        estado = request.form.get('uf_sede')
        rua = request.form.get('rua')
        bairro = request.form.get('bairro')
        atuacao = request.form.get('atuacao')
        tamanho = request.form.get('tamanho')
        fundacao = request.form.get('fundacao')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        site = request.form.get('site')
        descricao = request.form.get('descricao')

        bd.update({'empresa': int(session['empresa'])}, {
            '$set': {
                'cnpj': cnpj,
                'nome': nome_fantasia,
                'tamanho': int(tamanho),
                'fundacao': fundacao,
                'descricao': descricao,
                'endereco.rua': rua,
                'endereco.bairro': bairro,
                'endereco.cidade': cidade,
                'endereco.estado': estado,
                'contato.telefone': telefone,
                'contato.site': site,
                'contato.email': email,
                'atuacao': atuacao
            }
        })

        return redirect(url_for('rh.empresa'))

    empresa = list(bd.find({'empresa': int(session['empresa'])}))
    print(empresa[0]['endereco'])

    return render_template('rh/empresa.html', user=user, empresa=empresa)
