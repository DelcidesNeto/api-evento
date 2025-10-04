import requests
from time import sleep
requisicoes = 0
print('Iniciando requisições...')
while True:
    try:
        requests.get('https://api-evento-xf4o.onrender.com/')
        requisicoes += 1
        print(f'Requisição {requisicoes} feita com sucesso!')
        sleep(300)
    except Exception as e:
        print(f'Erro: {e}')
        input('')
