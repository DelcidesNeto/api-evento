import requests
from time import sleep
requisicoes = 0
print('Iniciando requisições...')
while True:
    requests.get('https://api-evento-xf4o.onrender.com/')
    requisicoes += 1
    print(f'Requisição {requisicoes} feita com sucesso!')
    sleep(300)
