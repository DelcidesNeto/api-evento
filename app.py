import requests
from flask import Flask, jsonify, request
app = Flask(__name__)


def formatar_celular(numero: str):
    numero_velho = numero.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
    numero_novo = '55'+numero_velho[0:2]+numero_velho[3:]
    return numero_novo


def enviar_localizacao(numero: str):
    headers = {
        'apiKey': '7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc'
    }
    body = {
        'number': numero,
        'name': 'Palácio Verde',
        'address': 'Av. Tancredo Neves, 100 - vila moreira, Itapuranga - GO, 76680-000',
        'latitude': -15.5545813,
        'longitude': -49.9406908
    }
    requests.post('https://chat.nside.com.br/message/sendLocation/556286427879-62986427879', headers=headers, json=body)


def enviar_imagem_com_texto(nome: str, numero: str):

    body_msg = f'''
Olá, {nome} !  

Sua inscrição no evento *Coffee Break – Reforma Tributária e TEF em Goiás* foi confirmada. ✅

📅 Data: 29/10 (Quarta-Feira)
⏰ Horário: 15h
📍 Local: Palácio Verde Eventos – Itapuranga/GO

Estamos ansiosos para te receber!  ☕📊'''
    headers = {
        'apiKey': '7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc'
    }
    body = {
        'number': numero,
        'mediatype': 'image',
        'mimetype': 'image/png',
        'caption': body_msg,
        'media': 'https://images2.imgbox.com/88/e3/RY031wPH_o.jpeg',
        'fileName': 'convite.png'
    }
    requests.post('https://chat.nside.com.br/message/sendMedia/556286427879-62986427879', headers=headers, json=body)


@app.route('/')
def homepage():
    return 'Welcome to the matto!'
@app.route('/enviar-confirmacao-de-presenca', methods=['POST'])
def envio():
    try:
        data = request.get_json()
        numero_formatado = formatar_celular(data['numero'])
        cidade = data['cidade']
        enviar_imagem_com_texto(data['nome'], numero_formatado)
        if cidade != 'ITAPURANGA':
            enviar_localizacao(numero_formatado)
        return jsonify({'status_request': 'ok'})
    except Exception as e:
        return jsonify({'status_request': f'error: {e}'})


if __name__ == '__main__':
    app.run(debug=True)
