# devs_tracelogger/log.py
import traceback
from datetime import datetime
import requests
import json
from devs_tracelogger.mongo import MongoLogger

class Log:
    def __init__(self, webhook: dict = {"id": int, "token": str}, default_user: str = "Sem responsável definido", bot_name: str = "Robô sem nome definido", send_notification: bool = True, mongo = None) -> None:
        """
        Inicializa o logger com um webhook do Discord e valores padrão para o robô e o responsável.

        Parâmetros:
        - webhook (dict): Dicionário contendo o 'id' e 'token' do webhook.
            - id (int): O ID do webhook (obrigatório).
            - token (str): O token do webhook (obrigatório).
        - default_user (str): Nome do responsável (padrão: "Sem responsável definido").
        - bot_name (str): Nome do robô ou serviço (padrão: "Robô sem nome definido").
        - send_notification (bool): Define se deve enviar a notificação ao Discord (padrão: True).
        - mongo (MongoLogger): Instância opcional do MongoLogger para gravar os logs no MongoDB.
        """
        if not isinstance(webhook, dict) or 'id' not in webhook or 'token' not in webhook:
            raise ValueError("O dicionário 'webhook' deve conter as chaves 'id' e 'token'.")
        
        if not isinstance(webhook['id'], int):
            raise ValueError("O valor de 'id' deve ser um número inteiro.")
        
        if not isinstance(webhook['token'], str):
            raise ValueError("O valor de 'token' deve ser uma string.")
        
        self.webhook_url = f"https://discord.com/api/webhooks/{webhook['id']}/{webhook['token']}"
        self.default_user = default_user
        self.bot_name = bot_name
        self.send_notification = send_notification
        self.mongo = mongo

    def register(self, e: Exception, arr: dict = None) -> None:
        """
        Registra o erro capturando os detalhes da exceção e envia para o Discord via webhook.
        """
        try:
            if arr is None:
                arr = {}

            tb = traceback.extract_tb(e.__traceback__)

            # Monta a estrutura de dados do erro
            error_data = {
                "filename": str(tb[-1].filename),
                "function": str(tb[-1].name),
                "type_error": str(type(e).__name__),
                "error": str(e),
                "line": tb[-1].lineno,
                "created_at": datetime.now(),
                "robo": arr.get('nome_robo', self.bot_name.upper()),
                "responsavel": arr.get('responsavel', self.default_user.upper())
            }

            # Envia a mensagem para o Discord
            mensagem = self.send_discord(error_data, arr.get('color', '15158332')) if self.send_notification else ''

            if self.mongo:
                m = MongoLogger(self.mongo['mongo_uri'], self.mongo['db_name'], self.mongo['collection_name'])
                m.log_error(error_data)
                del m

            return {"status":200, "data": error_data, "message": mensagem}
        except Exception as ex:
            return {"status":400, "error":str(ex)}

    def send_discord(self, error_data: dict, color) -> None:
        """
        Envia a mensagem de erro para um canal do Discord usando um webhook.
        """
        # Prepara a mensagem para o Discord
        data = {
            "embeds": [
                {
                    "title": "Problema",
                    "description": f":pushpin: {error_data['error']}",
                    "color": color,
                    "author": {
                        "name": error_data['robo'],
                        "icon_url": "https://w7.pngwing.com/pngs/567/444/png-transparent-robotics-chatbot-technology-robot-education-electronics-computer-program-humanoid-robot-thumbnail.png"
                    },
                    "fields": [
                        {"name": "Arquivo", "value": f":card_box: {error_data['filename']}", "inline": False},
                        {"name": "Linha", "value": str(error_data['line']), "inline": True},
                        {"name": "Função", "value": error_data['function'], "inline": True},
                        {"name": "Responsável", "value": error_data['responsavel'], "inline": False},
                        {"name": "Data e Hora", "value": f":calendar: {datetime.now().strftime('%d/%m/%Y %H:%M')}", "inline": False}
                    ]
                }
            ]
        }

        # Envia a requisição para o Discord
        response = requests.post(self.webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        
        if response.status_code == 204:
            return "Mensagem enviada com sucesso!"
        else:
            return f"Falha ao enviar a mensagem. Status code: {response.status_code}"
