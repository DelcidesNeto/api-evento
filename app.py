import requests
from flask import Flask, jsonify
app = Flask(__name__)


@app.route('/teste-envio-api')
def enviar_localizacao():
    headers = {
        'apiKey': '7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc'
    }
    body = {
        'number': '556293208952',
        'name': 'Palácio Verde',
        'address': 'Av. Tancredo Neves, 100 - vila moreira, Itapuranga - GO, 76680-000',
        'latitude': -15.5545813,
        'longitude': -49.9406908
    }
    requests.post('https://chat.nside.com.br/message/sendLocation/556285792072-356960', headers=headers, json=body)
    return jsonify({'opa': 'ok'})

if __name__ == '__main__':
    app.run()