from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, jsonify
)
from flask_cors import CORS, cross_origin
from bson.json_util import dumps
from bson.objectid import ObjectId
import datetime
from json import dump
import db as db
from candidatos import login_required_candidato

vagas = Blueprint('vagas', __name__, url_prefix='/api/vagas')

cors = CORS(vagas, resources={r"/get_vagas": {"origins": "http://127.0.0.1:3000"}})

bd_vagas = db.conn.hure.vagas
bd_candidatos = db.conn.hure.candidatos
bd_users = db.conn.hure.users


@vagas.route('/get-vagas/<int:idempresa>/', methods=['GET'])
@cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
def get_vagas(idempresa):
    bd = bd_vagas

    vg = list(bd.find({'empresa': idempresa}))
    json = dumps(vg)
    return json


@vagas.route('candidatar/', methods=['POST'])
@cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
@login_required_candidato
def candidatar():
    if request.method == 'POST':
        candidato = session['cand_id']
        bd = bd_candidatos
        vaga = bd_vagas
        id_vaga = request.form.get('id_vaga')
        print(id_vaga)
        empresa = request.form.get('empresa')
        nome_empresa = list(bd_users.find({'empresa': int(empresa)}, {'nome': 1}))
        hoje = datetime.datetime.now()

        vg = vaga.find_one({'_id': ObjectId(id_vaga)})
        print(vg)
        pgt1 = request.form.get('pergunta_pgt_1')
        seq1 = request.form.get('sequencia_pgt_1')
        res1 = request.form.get('resposta_pgt_1')

        pgt2 = request.form.get('pergunta_pgt_2')
        seq2 = request.form.get('sequencia_pgt_2')
        res2 = request.form.get('resposta_pgt_2')

        pgt3 = request.form.get('pergunta_pgt_3')
        seq3 = request.form.get('sequencia_pgt_3')
        res3 = request.form.get('resposta_pgt_3')

        pgt4 = request.form.get('pergunta_pgt_4')
        seq4 = request.form.get('sequencia_pgt_4')
        res4 = request.form.get('resposta_pgt_4')

        pgt5 = request.form.get('pergunta_pgt_5')
        seq5 = request.form.get('sequencia_pgt_5')
        res5 = request.form.get('resposta_pgt_5')

        pgt6 = request.form.get('pergunta_pgt_6')
        seq6 = request.form.get('sequencia_pgt_6')
        res6 = request.form.get('resposta_pgt_6')

        pgt7 = request.form.get('pergunta_pgt_7')
        seq7 = request.form.get('sequencia_pgt_7')
        res7 = request.form.get('resposta_pgt_7')
        
        respostas = [
            {
                'pgt': int(seq1) if seq1 is not None else None,
                'pergunta': pgt1,
                'resposta': res1
            },
            {
                'pgt': int(seq2) if seq2 is not None else None,
                'pergunta': pgt2,
                'resposta': res2
            },
            {
                'pgt': int(seq3) if seq3 is not None else None,
                'pergunta': pgt3,
                'resposta': res3
            },
            {
                'pgt': int(seq4) if seq4 is not None else None,
                'pergunta': pgt4,
                'resposta': res4
            },
            {
                'pgt': int(seq5) if seq5 is not None else None,
                'pergunta': pgt5,
                'resposta': res5
            },
            {
                'pgt': int(seq6) if seq6 is not None else None,
                'pergunta': pgt6,
                'resposta': res6
            },
            {
                'pgt': int(seq7) if seq7 is not None else None,
                'pergunta': pgt7,
                'resposta': res7
            }
        ]
        
        # verifica se o candidato já se candidatou para essa vaga antes
        verifica_cand = bd.find_one({'$and': [{'email': candidato}, {'candidaturas.id': ObjectId(id_vaga)}]})

        if verifica_cand is None:
            bd.update({'email': candidato}, {
                '$push': {
                    'candidaturas': {
                        'id': ObjectId(id_vaga),
                        'cargo': vg['cargo'],
                        'empresa': vg['empresa'],
                        'nome_empresa': nome_empresa[0]['nome'],
                        'cidade': vg['localizacao']['cidade'],
                        'estado': vg['localizacao']['estado'],
                        'respostas': respostas,
                        'status': 0,
                        'data': hoje
                    }
                }
            })
        else:
            print('Já candidatou-se')
            return redirect(url_for('person.login'))
        return redirect(url_for('person.curriculo'))


@vagas.route('vaga/<int:empresa>/<idvaga>/')
@cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
def vaga(empresa, idvaga):

    if request.method == 'GET':
        bd = bd_vagas
        vaga = bd.find_one({'$and': [{'empresa': empresa}, {'_id': ObjectId(idvaga)}, {'publicada': 1}]})

        if vaga is None:
            if session.get("empresa") is not None:
                return redirect(url_for('rh.painel'))
            else:
                return redirect(url_for('person.candidaturas'))
        else:
            bd = bd_vagas
            vaga = bd.find_one({'$and': [{'empresa': empresa}, {'_id': ObjectId(idvaga)}, {'publicada': 1}]})
            prazo = bd.find_one({'_id': ObjectId(vaga['_id'])}, {'prazo': 1})
            qtd = 0
            perguntas = vaga['qtd_perguntas']
            qtd = perguntas - 1

            if session.get('cand_id'):
                candidatou = list(bd_candidatos.find({'$and': [{'email': session['cand_id']},
                                                               {'candidaturas.id': ObjectId(idvaga)}]},
                                                     {'candidaturas': 1}))
            else:
                candidatou = None

            prazo = datetime.datetime.strptime(prazo['prazo'], '%Y-%m-%d').strftime('%d/%m/%Y')

            bd = bd_users
            emp = bd.find_one({'empresa': empresa})
            print(emp)

            return render_template('vagas/vaga.html', vaga=vaga, prazo=prazo, perguntas=qtd, empresa=emp, candidatou=candidatou)


@vagas.route('empresa/<int:empresa>/<nome_empresa>')
def empresa(empresa, nome_empresa):
    if request.method == 'GET':
        bd = bd_vagas
        vagas = list(bd.find({'$and': [{'empresa': empresa}, {'publicada': 1}]}))

        bd = bd_users
        emp = bd.find_one({'empresa': empresa})

        return render_template('vagas/empresa.html', vagas=vagas, empresa=empresa, dados_empresa=emp)


@vagas.route('/verifica-cand-email/', methods=['POST'])
@cross_origin(origin='localhost', headers=['Content-Type','Authorization'])
def verifica_cand_email():
    bd = bd_candidatos
    query = request.form.get('email')
    # busca = re.compile(f'.*{query}*.', re.IGNORECASE)

    print(f'EMAIL:{query}')

    candidatos = list(bd.find({'email': query}, {'email': 1}))

    return JSONEncoder().encode(candidatos[0])