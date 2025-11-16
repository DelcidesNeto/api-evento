#https://images2.imgbox.com/f5/35/xaPtCjC8_o.jpeg Imagem 3 dias
#https://images2.imgbox.com/0d/4d/r2A4uPU4_o.jpeg Imagem do dia
#https://images2.imgbox.com/93/18/2YSL1eV9_o.jpeg Imagem é amanhã
import pandas as pd
from random import randint
from time import sleep
import os, json, requests, pytz
from datetime import datetime, time

def formatar_celular(numero: str):
    numero_velho = numero.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
    numero_novo = '55'+numero_velho[0:2]+numero_velho[3:]
    return numero_novo

def enviou_mensagem(telefone: str):
    if not os.path.exists('enviados.json'):
        with open('enviados.json', "wt+", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    with open('enviados.json', "r", encoding="utf-8") as arq:
        enviados = json.load(arq)
        if telefone not in enviados:
            return False
        else:
            return True


def adicionar(telefone: str):
    with open('enviados.json', "r", encoding="utf-8") as arq:
        enviados = json.load(arq)
        enviados[telefone] = True
        with open('enviados.json', "wt+", encoding="utf-8") as arqjson:
            json.dump(enviados, arqjson, indent=4, ensure_ascii=False)
    
def enviar_imagem_com_texto(nome: str, numero: str, sessao: str):

    body_msg = f'''🎉 É AMANHÃ {nome}!

Está chegando o dia do Coffee Break NETSide ☕
Um encontro especial pra falarmos sobre as mudanças da Reforma Tributária e a obrigatoriedade do TEF em Goiás 💳

📅 É amanhã dia 29 de outubro (Quarta-feira)
📍 Palácio Verde Eventos – Itapuranga-GO
🕒 A partir das 15h

🎙️ Palestrantes:
* Marcelo Couto – COO da Destaxa
* Juliano Malheiros – Empresário Contábil

✅ Evento gratuito com muito conteúdo e aquele café especial esperando por você!
Nos vemos lá 👋'''
    
    headers = {
        'apiKey': '7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc'
    }
    body = {
        'number': numero,
        'mediatype': 'image',
        'mimetype': 'image/png',
        'caption': body_msg,
        'media': 'https://images2.imgbox.com/93/18/2YSL1eV9_o.jpeg',
        'fileName': 'convite.png'
    }
    requests.post(f'https://chat.nside.com.br/message/sendMedia/{sessao}', headers=headers, json=body)        


planilha = pd.read_csv('InscricaoCB - CB.csv')
nomes_clientes = planilha['Nome']
dias_da_semana = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
while True:
    dia_da_semana = dias_da_semana[datetime.today().astimezone(pytz.timezone('America/Sao_Paulo')).weekday()]
    if dia_da_semana == 'Terça':
        if datetime.today().astimezone(pytz.timezone('America/Sao_Paulo')).now().time() >= time(8, 0):
            for i, nome in enumerate(nomes_clientes):
                # numero = '556285792072'
                numero = formatar_celular(planilha['WhatsApp'][i])
                if not enviou_mensagem(numero):
                    esperar = randint(120, 210)
                    sleep(esperar)
                    adicionar(numero)
                    enviar_imagem_com_texto(nome, numero, '556286427879-62986427879')
                    print(f'Mensagem enviada para {nome} Nº {numero}')
            break
