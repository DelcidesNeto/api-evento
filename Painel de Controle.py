import customtkinter as ctk
import threading
import requests
import json
import pytz
import os
from datetime import datetime, time
import socketio
from time import time as tempo_api
from time import sleep

# ==========================================
# CONFIGURAÇÕES
# ==========================================
clientes_que_chamaram = {}
FERIADOS_FILE = os.path.join(os.getcwd(), "feriados_personalizados.json")
URL_API = "https://api-evento-xf4o.onrender.com/"
URL_WS = "https://chat.nside.com.br"
instancia_nova = "telefone-sistemas"
instancia_antiga = '556286427879-62986427879'
APIKEY = "7hiEkUh2qbCNzoPSndk6vOnFvCmsVwILhN7xdJPVhgju8nagew8XD4DiytCyXg0dSzMpDafWhoc"
# ----------------Para testes ----------------------
# URL_WS = "http://localhost:8080"
# instancia_nova = "t2"
# instancia_antiga = 't1'
# APIKEY = "429683C4C977415CAAFCCE10F7D57E11"
ws_rodando = False


# ==========================================
# CLASSE PRINCIPAL
# ==========================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel de Controle v1.1.0")
        self.iconbitmap(self.resource_path('recarregar.ico'))
        self.geometry("600x850")
        ctk.set_appearance_mode("dark")

        # SocketIO client
        self.sio = socketio.Client()

        # Estrutura do layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)  # logs expande verticalmente

        self.create_ws_section()
        self.create_requisicao_section()
        self.create_feriados_section()
        self.create_logs_section()

        self.requisicoes_ativas = False
        self.carregar_feriados()
        self.iniciar_ws_thread()
        # self.toggle_requisicoes()
    # =========================================
    # Seção funções do WebSocket
    # =========================================
    def resource_path(self, relative_path):
        import sys
        """Pega o caminho absoluto do recurso, funciona no .exe e no .py"""
        try:
            # PyInstaller cria uma pasta temporária e guarda em _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    def e_grupo(self, dados: dict):
            #id_participante_grupo = dados['data']['key']['participant']
            numero = dados['data']['key']['remoteJid']
            if '@g' in numero:
                return True
            else:
                return False
            
    def formatar_numero(self, req):
        # index = numero.find('@')
        # return numero[0:index]
        try:
            numero = req['data']['key']['senderPn']
            index = numero.find('@')
            return numero[0:index]
        except:
            numero = req['data']['key']['remoteJid']
            index = numero.find('@')
            return numero[0:index]

    def enviar_mensagem_cliente(self, numero: str, instancia: str, body_msg=''): # passe a instancia do número novo
        if body_msg == '':
            data_hoje = datetime.today().astimezone(pytz.timezone('America/Sao_Paulo'))
            data_log = data_hoje.strftime('%d/%m/%Y %H:%M:%S')
            # hora_minuto = data_hoje.now().time()
            # if hora_minuto < time(12, 0):
            #     periodo = 'Bom dia'
            # elif hora_minuto >= time(12, 0) and hora_minuto < time(19, 0):
            #     periodo = 'Boa tarde'
            # else:
            #     periodo = 'Boa Noite'
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
            'number': numero,
            'text': body_msg
        }
        requests.post(f'{URL_WS}/message/sendText/{instancia}', headers=headers, json=body)

    def enviar_mensagem_grupo(self, numero: str): # instancia do número velho

        body_msg = f'''O número *{numero}* entrou em contato pelo nosso número antigo, verifique se ele caiu no aguardando, caso não tenha caído alguém chame-o por favor...'''
        headers = {
            'apiKey': APIKEY
        }
        body = {
            'number': '120363405878579813',
            'text': body_msg
        }
        requests.post(f'{URL_WS}/message/sendText/{instancia_nova}', headers=headers, json=body)


    def foi_eu_que_mandei(self, dados: dict):
        if dados['data']['key']['fromMe'] == True:
            return True
        else:
            return False
        
    def e_feriado(self, data):
        with open(FERIADOS_FILE, 'rt', encoding='utf-8') as arq_json:
            feriados_json = json.load(arq_json)
            if data in feriados_json:
                return feriados_json[data]
            else:
                return ''
    def adiconar_log_arq(self, log: str):
        with open('log.txt', 'at', encoding='utf-8') as arq:
            arq.write(log)
    def e_horario_comercial(self, numero: str):
        result = True
        dias_da_semana = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        data_hoje = datetime.today().astimezone(pytz.timezone('America/Sao_Paulo'))
        data_log = data_hoje.strftime('%d/%m/%Y %H:%M:%S')
        dia_da_semana = dias_da_semana[data_hoje.weekday()]
        hora_minuto = data_hoje.now().time()
        # if hora_minuto < time(12, 0):
        #     periodo = 'Bom dia'
        # elif hora_minuto >= time(12, 0) and hora_minuto < time(19, 0):
        #     periodo = 'Boa tarde'
        # else:
        #     periodo = 'Boa Noite'
        e_feriado = self.e_feriado(data_hoje.strftime('%d/%m/%Y'))
        if e_feriado != '':
            hora_inicio = e_feriado['inicio'].split(':')
            hora_fim = e_feriado['fim'].split(':')
            if hora_minuto < time(int(hora_inicio[0]), int(hora_inicio[1])+1):
                body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Hoje nossos atendimentos iniciam à partir das {hora_inicio[0]}:{hora_inicio[1]}.

_Você será atendido após as {hora_inicio[0]}:{hora_inicio[1]}*, por favor aguarde..._'''
                self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
                self.enviar_mensagem_grupo(numero)
                result = False
            elif hora_minuto > time(int(hora_fim[0]), int(hora_fim[1])+1):
                body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Notamos também que você entrou em contato conosco *após as {hora_fim[0]}:{hora_fim[1]}*.

Infelizmente nossos atendimentos por hoje estão encerrados, porém seu atendimento já foi transferido para o nosso setor de *SUPORTE*, e você será atendido no próximo dia útil à partir das 07:30'''
                self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
                self.enviar_mensagem_grupo(numero)
                result = False
        elif dia_da_semana == 'Sábado':
            if hora_minuto < time(7, 30+1):
                body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Hoje nossos atendimentos iniciam à partir das 07:30.

_*Você será atendido após as 07:30*, por favor aguarde..._'''
                self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
                self.enviar_mensagem_grupo(numero)
                result = False
            elif hora_minuto > time(18, 30+1):
                body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

Notamos que mandou uma mensagem no contato do financeiro (62)98642-7879. Sempre que precisar de suporte pode priorizar esses dois números:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Notamos também que você entrou em contato conosco *após as 18:30*.

Infelizmente nossos atendimentos por hoje estão encerrados, porém seu atendimento já foi transferido para o nosso setor de *SUPORTE* você será atendido no próximo dia útil à partir das 07:30, tenha uma boa noite!'''
                self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
                self.enviar_mensagem_grupo(numero)
                result = False
        elif dia_da_semana == 'Domingo':
            # if hora_minuto > time(13, 0)+1:
            body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Infelizmente nossos atendimentos por hoje estão encerrados, porém seu atendimento já foi transferido para o nosso setor de *SUPORTE* você será atendido no próximo dia útil à partir das 07:30.
Tenha um bom Domingo!'''
            self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
            self.enviar_mensagem_grupo(numero)
            result = False
#         elif hora_minuto < time(8, 0+1):
#             body_msg = f'''*[{data_log}]*

# Olá ! Tudo bem?

#         Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
# - (62) 3312-1502 -- WhatsApp e chamadas
# - (62) 99357-2050 - Somente WhatsApp


# Hoje nossos atendimentos iniciam à partir das 08:00.

# _*Você será atendido após as 08:00*, por favor aguarde..._'''
#             self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
#             self.enviar_mensagem_grupo(numero)
#             result = False
        else:
            if hora_minuto < time(7, 30+1):
                body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Hoje nossos atendimentos iniciam à partir das 07:30.

_*Você será atendido após as 07:30*, por favor aguarde..._'''
                self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
                self.enviar_mensagem_grupo(numero)
                result = False
            elif hora_minuto > time(22, 0+1):
                body_msg = f'''*[{data_log}]*

Olá ! Tudo bem?

          Notamos que mandou uma mensagem em nosso contato destinado ao FINANCEIRO (62) 98642-7879. Sempre que precisar de SUPORTE pode priorizar esses dois contatos:
- (62) 3312-1502 -- WhatsApp e chamadas 
- (62) 99357-2050 - Somente WhatsApp


Notamos também que você entrou em contato conosco *após as 22:00*.

Infelizmente nossos atendimentos por hoje estão encerrados, porém seu atendimento já foi transferido para o nosso setor de *SUPORTE* você será atendido no próximo dia útil à partir das 07:30.

Tenha uma boa noite de sono!'''
                self.enviar_mensagem_cliente(numero=numero, instancia=instancia_nova, body_msg=body_msg)
                self.enviar_mensagem_grupo(numero)
                result = False
        return result


    # ==========================================
    # Seção de WebSocket
    # ==========================================
    def create_ws_section(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="WebSocket", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=5)
        self.status_ws = ctk.CTkLabel(frame, text="Desconectado!", text_color="red")
        self.status_ws.grid(row=1, column=0, pady=5)

        self.btn_ws = ctk.CTkButton(frame, text="Iniciar Conexão", command=self.iniciar_ws_thread)
        self.btn_ws.grid(row=2, column=0, pady=10)

    def iniciar_ws_thread(self):
        threading.Thread(target=self.iniciar_ws, daemon=True).start()

    def iniciar_ws(self):
        global ws_rodando
        try:
            self.status_ws.configure(text="Conectando...", text_color="yellow")
            if not ws_rodando:
                self.log("Tentando conectar ao WebSocket...")
                self.sio.connect(f"{URL_WS}/{instancia_antiga}", transports=['websocket'], headers={'apiKey': APIKEY})
                ws_rodando = True
                self.status_ws.configure(text="Conectado!", text_color="green")
                self.log("✅ Conectado ao WebSocket com sucesso!")
                self.btn_ws.configure(text='Desconectar')
                threading.Thread(target=self.iniciar_observacao_do_ws, daemon=True).start()
            else:
                self.sio.disconnect()
                ws_rodando = False
                self.status_ws.configure(text="Desconectado!", text_color="red")
                self.log(f'⛔ WebSocket desconectado.')
                self.btn_ws.configure(text='Iniciar Conexão')
        except Exception as e:
            if 'Already connected' not in str(e):
                self.status_ws.configure(text=f"Erro: {e}", text_color="red")
                self.log(f"❌ Erro ao conectar WebSocket: {e}")

    
    
    def iniciar_observacao_do_ws(self):
        def procedure(req):
            instancia_api = req['instance']
            if instancia_api == instancia_antiga:
                if not self.e_grupo(req) and not self.foi_eu_que_mandei(req):
                    numero_api = req['data']['key']['remoteJid']
                    data_log = datetime.today().astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
                    log_arq = f'---------------------------\n{data_log}\nJson: {req}\nNumero de telefone original sem formatação para análise: {numero_api}\n---------------------------\n'
                    self.adiconar_log_arq(log_arq)
                    numero_formatado = self.formatar_numero(req)
                    data_hora_que_chamou = tempo_api()
                    if numero_api in clientes_que_chamaram:
                        ultima_mensagem_recebida = (data_hora_que_chamou-clientes_que_chamaram[numero_api])/60
                        if ultima_mensagem_recebida >= 15:
                            clientes_que_chamaram[numero_api] = data_hora_que_chamou
                            if self.e_horario_comercial(numero_formatado):
                                self.enviar_mensagem_cliente(numero=numero_formatado, instancia=instancia_nova)
                                self.enviar_mensagem_grupo(numero_formatado)
                    else:
                        clientes_que_chamaram[numero_api] = data_hora_que_chamou
                        if self.e_horario_comercial(numero_formatado):
                            self.enviar_mensagem_cliente(numero=numero_formatado, instancia=instancia_nova)
                            self.enviar_mensagem_grupo(numero_formatado)
        @self.sio.on('messages.upsert')
        def mensagem_recebida(req):
            threading.Thread(target=procedure, args=(req,), daemon=True).start()

    # ==========================================
    # Seção de Requisições GET
    # ==========================================
    def create_requisicao_section(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Requisições Periódicas", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=5)
        self.status_req = ctk.CTkLabel(frame, text="Parado", text_color="red")
        self.status_req.grid(row=1, column=0, pady=5)

        self.btn_req = ctk.CTkButton(frame, text="Iniciar Requisições", command=self.toggle_requisicoes)
        self.btn_req.grid(row=2, column=0, pady=10)

    def toggle_requisicoes(self):
        self.requisicoes_ativas = not self.requisicoes_ativas
        if self.requisicoes_ativas:
            self.status_req.configure(text="Executando...", text_color="green")
            self.btn_req.configure(text="Parar Requisições")
            threading.Thread(target=self.loop_requisicoes, daemon=True).start()
        else:
            self.status_req.configure(text="Parado", text_color="red")
            self.btn_req.configure(text="Iniciar Requisições")
            self.log("⛔ Requisições periódicas paradas.")

    def loop_requisicoes(self):
        contador = 0
        while self.requisicoes_ativas:
            try:
                requests.get(URL_API)
                contador += 1
                self.status_req.configure(text=f"Requisição {contador} OK", text_color="green")
                self.log(f"✅ Requisição {contador} enviada com sucesso.")
            except Exception as e:
                self.status_req.configure(text=f"Erro: {e}", text_color="red")
                self.log(f"❌ Erro ao fazer requisição: {e}")
            sleep(300)  # 5 minutos

    # ==========================================
    # Seção de Feriados (centralizada)
    # ==========================================
    def create_feriados_section(self):
        frame_outer = ctk.CTkFrame(self, corner_radius=10)
        frame_outer.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(frame_outer, text="Feriados Personalizados", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Frame interno centralizado
        frame = ctk.CTkFrame(frame_outer, fg_color="transparent")
        frame.pack(pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        self.select_feriado = ctk.CTkOptionMenu(frame, values=["Nenhum"], command=self.preencher_campos)
        self.select_feriado.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        ctk.CTkLabel(frame, text="Nome Feriado:").grid(row=1, column=0, pady=5, sticky="e")
        self.entry_nome_feriado = ctk.CTkEntry(frame, width=150)
        self.entry_nome_feriado.grid(row=1, column=1, pady=5, sticky="w")

        ctk.CTkLabel(frame, text="Data (DD/MM/YYYY):").grid(row=2, column=0, pady=5, sticky="e")
        self.entry_data = ctk.CTkEntry(frame, width=150)
        self.entry_data.grid(row=2, column=1, pady=5, sticky="w")
        self.entry_data.bind("<KeyRelease>", self.formatar_data)

        ctk.CTkLabel(frame, text="Início:").grid(row=3, column=0, pady=5, sticky="e")
        self.entry_inicio = ctk.CTkEntry(frame, width=150)
        self.entry_inicio.grid(row=3, column=1, pady=5, sticky="w")
        self.entry_inicio.bind("<KeyRelease>", self.formatar_hora)

        ctk.CTkLabel(frame, text="Fim:").grid(row=4, column=0, pady=5, sticky="e")
        self.entry_fim = ctk.CTkEntry(frame, width=150)
        self.entry_fim.grid(row=4, column=1, pady=5, sticky="w")
        self.entry_fim.bind("<KeyRelease>", self.formatar_hora)

        self.btn_salvar = ctk.CTkButton(frame, text="Salvar / Atualizar", command=self.salvar_feriado)
        self.btn_salvar.grid(row=5, column=0, pady=10, columnspan=2)

        self.btn_excluir = ctk.CTkButton(frame, text="Excluir", fg_color="red", command=self.excluir_feriado)
        self.btn_excluir.grid(row=6, column=0, pady=5, columnspan=2)

    def formatar_hora(self, event):
        entry = event.widget
        texto = entry.get()
        numeros = [c for c in texto if c.isdigit()]

        # Limita a 4 dígitos (HHMM)
        numeros = numeros[:4]

        # Formata para HH:MM
        hora_formatada = ""
        for i, n in enumerate(numeros):
            if i == 2:
                hora_formatada += ":"
            hora_formatada += n

        # Atualiza o campo sem mover o cursor para o fim
        entry.delete(0, "end")
        entry.insert(0, hora_formatada)
    def formatar_data(self, event):
        texto = self.entry_data.get()
        numeros = [c for c in texto if c.isdigit()]

        # Limita a 8 dígitos (DDMMYYYY)
        numeros = numeros[:8]

        # Formata para DD/MM/YYYY
        data_formatada = ""
        for i, n in enumerate(numeros):
            if i == 2 or i == 4:
                data_formatada += "/"
            data_formatada += n

        # Atualiza o campo sem mover o cursor para o fim
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, data_formatada)
    def carregar_feriados(self):
        if not os.path.exists(FERIADOS_FILE):
            with open(FERIADOS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

        with open(FERIADOS_FILE, "r", encoding="utf-8") as f:
            self.feriados = json.load(f)

        self.atualizar_select()
        self.log("📅 Feriados carregados com sucesso.")

    def atualizar_select(self):
        if self.feriados:
            self.select_feriado.configure(values=list(self.feriados.keys()))
        else:
            self.select_feriado.configure(values=["Nenhum"])

    def preencher_campos(self, data):
        if data not in self.feriados:
            return
        self.entry_nome_feriado.delete(0, 'end')
        feriado = self.feriados[data]
        self.entry_data.delete(0, "end")
        self.entry_inicio.delete(0, "end")
        self.entry_fim.delete(0, "end")
        

        self.entry_nome_feriado.insert(0, feriado['nome'])
        self.entry_data.insert(0, data)
        self.entry_inicio.insert(0, feriado['inicio'])
        self.entry_fim.insert(0, feriado['fim'])

    def salvar_feriado(self):
        data = self.entry_data.get().strip()
        inicio = self.entry_inicio.get().strip()
        fim = self.entry_fim.get().strip()
        nome = self.entry_nome_feriado.get()

        if not data:
            self.log("⚠️ Data inválida, não foi possível salvar.")
            return

        self.feriados[data] = {
            "nome": nome,
            "inicio": inicio,
            "fim": fim
        }

        with open(FERIADOS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.feriados, f, indent=2, ensure_ascii=False)

        self.atualizar_select()
        self.select_feriado.set(data)
        self.log(f"💾 Feriado {data} salvo/atualizado com sucesso.")

    def excluir_feriado(self):
        data = self.select_feriado.get()
        if data in self.feriados:
            del self.feriados[data]
            with open(FERIADOS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.feriados, f, indent=2, ensure_ascii=False)
            self.entry_nome_feriado.delete(0, 'end')
            self.entry_data.delete(0, "end")
            self.entry_inicio.delete(0, "end")
            self.entry_fim.delete(0, "end")
            self.atualizar_select()
            self.select_feriado.set('Nenhum')

            self.log(f"🗑️ Feriado {data} excluído com sucesso.")

    # ==========================================
    # Seção de Logs
    # ==========================================
    def create_logs_section(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Logs do Sistema", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=5)

        self.log_textbox = ctk.CTkTextbox(frame, height=150, width=760, state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    def log(self, texto):
        """Adiciona uma linha no log"""
        self.log_textbox.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {texto}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")


# ==========================================
# EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    app = App()
    app.mainloop()
