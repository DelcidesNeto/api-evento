from datetime import datetime
import pytz, requests
data_hoje = datetime.today().astimezone(pytz.timezone('America/Sao_Paulo'))
data_log = data_hoje.strftime('%d/%m/%Y %H:%M:%S')
# hora_minuto = data_hoje.now().time()
# if hora_minuto < time(12, 0):
#     periodo = 'Bom dia'
# elif hora_minuto >= time(12, 0) and hora_minuto < time(19, 0):
#     periodo = 'Boa tarde'
# else:
#     periodo = 'Boa Noite'
URL_API = "https://api-evento-xf4o.onrender.com/"
URL_WS = "https://chat.nside.com.br"
instancia_nova = "telefone-sistemas"
instancia_antiga = '556286427879-62986427879'
APIKEY = "7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc"
body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?  

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


_Aguarde. Você está sendo transferido para um atendente humano..._'''
headers = {
    'apiKey': APIKEY
}
body = {
    'number': '556283425113',
    'text': body_msg
}
requests.post(f'{URL_WS}/message/sendText/{instancia_nova}', headers=headers, json=body)

body_msg = f'''O número *556283425113* entrou em contato pelo nosso número antigo, verifique se ele caiu no aguardando, caso não tenha caído alguém chame-o por favor...'''
headers = {
    'apiKey': APIKEY
}
body = {
    'number': '120363405878579813',
    'text': body_msg
}
requests.post(f'{URL_WS}/message/sendText/{instancia_nova}', headers=headers, json=body)