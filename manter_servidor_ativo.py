import requests
import socketio
from datetime import datetime, time
import pytz, os, json

sio = socketio.Client()

url = 'https://chat.nside.com.br'
instancia_antiga = '556285792072-356960'
instancia_nova = '556285792072-356960'
apiKey = '7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc'

clientes_que_chamaram = {}

def e_grupo(dados: dict):
    try:
        id_participante_grupo = dados['data']['key']['participant']
        return True
    except:
        return False


def foi_eu_que_mandei(dados: dict):
    if dados['data']['key']['fromMe'] == True:
        return True
    else:
        return False


def inicar_web_socket():

    payload = {
        "websocket": {
            "enabled": True,
            "events": [
                "APPLICATION_STARTUP",
                "QRCODE_UPDATED",
                "MESSAGES_UPSERT",
                "CONNECTION_UPDATE"
            ]
        }
    }

    res = requests.post(
        f"{url}/websocket/set/{instancia_antiga}",
        headers={"Content-Type": "application/json", "apikey": apiKey},
        json=payload
    )
    print(res)


def formatar_numero(numero: str):
    index = numero.find('@')
    return numero[0:index]


def e_feriado(data):
    with open(f'{os.getcwd()}\\feriados_personalizados.json', 'rt', encoding='utf-8') as arq_json:
        feriados_json = json.load(arq_json)
        if data in feriados_json:
            return True
        else:
            return False
    
def e_horario_comercial(numero: str):
    result = True
    dias_da_semana = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
    data_hoje = datetime.today().astimezone(pytz.timezone('America/Sao_Paulo'))
    dia_da_semana = dias_da_semana[data_hoje.weekday()]
    hora_minuto = data_hoje.now().time()
    if dia_da_semana == 'Sábado':
        if hora_minuto < time(7, 30):
            body_msg = f'''Vimos que você mandou uma mensagem no contato do financeiro, sempre que precisar de suporte pode priorizar esses dois números:
- (62) 3312-1502 — WhatsApp e chamadas 
- (62) 99357-2050 — Somente WhatsApp
Hoje nossos atendimentos iniciam à partir das 07:30.
*Você será atendido após as 07:30*, por favor aguarde...'''
            enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
            enviar_mensagem_grupo(numero)
            result = False
        elif hora_minuto > time(18, 30):
            body_msg = '''Boa tarde, tudo bem?
Vimos que você entrou em contato conosco *após as 18:30*.
Infelizmente nossos atendimentos por hoje estão encerrados, entre em contato conosco no Domingo à partir das 08:00 que auxiliaremos você.
Tenha, um bom final de semana!'''
            enviar_mensagem_cliente(numero=numero, instancia=instancia_antiga, body_msg=body_msg)
            result = False
    elif dia_da_semana == 'Domingo':
        if hora_minuto > time(13, 0):
            body_msg = '''Boa tarde, tudo bem?
Vimos que você entrou em contato conosco *após as 13:00*.
Infelizmente nossos atendimentos por hoje estão encerrados, entre em contato conosco na Segunda-Feira à partir das 07:30 que auxiliaremos você.
Tenha, um bom Domingo!'''
            enviar_mensagem_cliente(numero=numero, instancia=instancia_antiga, body_msg=body_msg)
            result = False
        elif hora_minuto < time(8, 0):
            body_msg = f'''Bom dia, tudo bem?
Vimos que você mandou uma mensagem no contato do financeiro, sempre que precisar de suporte pode priorizar esses dois números:
- (62) 3312-1502 — WhatsApp e chamadas 
- (62) 99357-2050 — Somente WhatsApp
Hoje nossos atendimentos iniciam à partir das 08:00.
*Você será atendido após as 08:00*, por favor aguarde...'''
            enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
            enviar_mensagem_grupo(numero)
            result = False
    else:
        if hora_minuto < time(7, 30):
            body_msg = f'''Vimos que você mandou uma mensagem no contato do financeiro, sempre que precisar de suporte pode priorizar esses dois números:
- (62) 3312-1502 — WhatsApp e chamadas 
- (62) 99357-2050 — Somente WhatsApp
Hoje nossos atendimentos iniciam à partir das 07:30.
*Você será atendido após as 07:30*, por favor aguarde...'''
            enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
            enviar_mensagem_grupo(numero)
            result = False
        elif hora_minuto > time(22, 0):
            body_msg = '''Boa noite, tudo bem?
Vimos que você entrou em contato conosco *após as 22:00*.
Infelizmente nossos atendimentos por hoje estão encerrados, entre em contato conosco no amanhã à partir das 07:30 que auxiliaremos você.
Tenha, uma boa noite de sono!'''
            enviar_mensagem_cliente(numero=numero, instancia=instancia_antiga, body_msg=body_msg)
            result = False
    return result


def enviar_mensagem_cliente(numero: str, instancia: str, body_msg=''): # passe a instancia do número novo
    if body_msg == '':
        body_msg = f'''Olá!  
Vimos que você mandou uma mensagem no contato do financeiro, sempre que precisar de suporte pode priorizar esses dois números:
- (62) 3312-1502 — WhatsApp e chamadas 
- (62) 99357-2050 — Somente WhatsApp
*Já estamos transferindo você para um atendente, um momento...*'''
    headers = {
        'apiKey': apiKey
    }
    body = {
        'number': numero,
        'text': body_msg
    }
    requests.post(f'{url}/message/sendText/{instancia}', headers=headers, json=body)

def enviar_mensagem_grupo(numero: str): # instancia do número velho

    body_msg = f'''O número *{numero}* entrou em contato pelo nosso número antigo, verifique se ele caiu no aguardando, caso não tenha caído alguém chame-o por favor...'''
    headers = {
        'apiKey': apiKey
    }
    body = {
        'number': '120363405878579813',
        'text': body_msg
    }
    requests.post(f'{url}/message/sendText/{instancia_nova}', headers=headers, json=body)


@sio.on('messages.upsert')
def mensagem_recebida(req):
    instancia = req['instance']
    if instancia == instancia_antiga:
        if not e_grupo(req): #and not foi_eu_que_mandei(req)
            numero_api = req['data']['key']['remoteJid']
            numero_formatado = formatar_numero(numero_api)
            data_hora_que_chamou = time()
            if numero_api in clientes_que_chamaram:
                ultima_mensagem_recebida = (data_hora_que_chamou-clientes_que_chamaram[numero_api])/60
                if ultima_mensagem_recebida >= 15:
                    clientes_que_chamaram[numero_api] = data_hora_que_chamou
                    #enviar_mensagem_grupo
                    if e_horario_comercial(numero_formatado):
                        enviar_mensagem_grupo(numero_formatado)
                        enviar_mensagem_cliente(numero_formatado, instancia_nova)
            else:
                clientes_que_chamaram[numero_api] = data_hora_que_chamou
                #enviar_mensagem_grupo
                if e_horario_comercial(numero_formatado):
                    enviar_mensagem_grupo(numero_formatado)
                    enviar_mensagem_cliente(numero_formatado, instancia_nova)

# @sio.on('*')
# def qualquer_evento(event, data):
#     print(f'Evento: {event}')
#     print(data)

@sio.event
def connect():
    print('Conectadado ao websocket!')


@sio.event
def disconnect():
    print('desconectado')


#inicar_web_socket()
# data_hoje = datetime.today().astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y')
# if e_feriado(data_hoje):
#     print('é feriado')
# else:
#     print('Não é feriado')
sio.connect(f'{url}/{instancia_antiga}', transports=['websocket'])
sio.wait()
# from time import sleep
# requisicoes = 0
# print('Iniciando requisições...')
# while True:
#     try:
#         requests.get('https://api-evento-xf4o.onrender.com/')
#         requisicoes += 1
#         print(f'Requisição {requisicoes} feita com sucesso!')
#         sleep(300)
#     except Exception as e:
#         print(f'Erro: {e}')
#         input('')
