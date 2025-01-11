# GrupoB Trace Logger

**GrupoB Trace Logger** é uma biblioteca Python fácil de usar para registrar exceções e enviar mensagens diretamente para um canal do Discord via Webhook. Ideal para monitorar e gerenciar erros em aplicações de forma prática, com integração automática ao Discord.

## Instalação

Instale a biblioteca usando `pip`:

```bash
pip install devs_tracelogger
```

## Como Usar

Abaixo estão exemplos de como usar a biblioteca para capturar exceções e enviar notificações ao Discord.

### Uso Básico

O exemplo a seguir mostra como criar uma instância da classe `Log` e registrar uma exceção diretamente no Discord:

```python
from devs_tracelogger import Log

try:
    marionette = Marionette()  # Exemplo de código que pode gerar uma exceção
except Exception as ex:
    log = Log(
        webhook={"id": 123456789012345678, "token": "exemploDeToken12345"},
        default_user="Gelson Júnior",  # Nome do responsável
        bot_name="Calculadora"  # Nome do robô ou serviço executando
    )
    log.register(ex)  # Registra a exceção e envia a mensagem para o Discord
```

Caso você não deseje enviar a mensagem ao Discord, defina o parâmetro `send_notification` como `False`. Por padrão, ele está definido como `True`.

### Uso com Parâmetros Dinâmicos

Os parâmetros também podem ser passados diretamente no método `register`. Quando valores são passados tanto no construtor quanto no método, os valores passados no `register` serão priorizados:

```python
from devs_tracelogger import Log

try:
    1 / 0  # Exemplo de código que pode gerar uma exceção
except Exception as ex:
    #Definir apenas se desejar salvar o log no banco
    mongo_logger = {
        "mongo_uri":"mongodb://localhost:27017",
        "db_name":"error_logs",
        "collection_name":"logs"
    }

    log = Log(
        webhook={"id": 123456789012345678, "token": "exemploDeToken12345"},
        mongo=mongo_logger #Opicional, definir apenas se quiser salvar o log no banco
    )
    log.register(
        ex,
        {
            "nome_robo": "Projeto Z",  # Nome do robô ou serviço
            "responsavel": "Gelson Júnior",  # Nome do responsável pelo código
            "color": "1752220" # cor deve ser em INT Color, formato que o discord aceita
        }
    )
```

### Cores sugerida

| Name                | INT Color | Hex Code  |
|---------------------|:---------:|:---------:|
| `Default`           |     0     | `#000000` |
| `Aqua`              |  1752220  | `#1ABC9C` |
| `DarkAqua`          |  1146986  | `#11806A` |
| `Green`             |  5763719  | `#57F287` |
| `DarkGreen`         |  2067276  | `#1F8B4C` |
| `Blue`              |  3447003  | `#3498DB` |
| `DarkBlue`          |  2123412  | `#206694` |
| `Purple`            | 10181046  | `#9B59B6` |
| `DarkPurple`        |  7419530  | `#71368A` |
| `LuminousVividPink` | 15277667  | `#E91E63` |
| `DarkVividPink`     | 11342935  | `#AD1457` |
| `Gold`              | 15844367  | `#F1C40F` |
| `DarkGold`          | 12745742  | `#C27C0E` |
| `Orange`            | 15105570  | `#E67E22` |
| `DarkOrange`        | 11027200  | `#A84300` |
| `Red`               | 15548997  | `#ED4245` |
| `DarkRed`           | 10038562  | `#992D22` |
| `Grey`              |  9807270  | `#95A5A6` |
| `DarkGrey`          |  9936031  | `#979C9F` |
| `DarkerGrey`        |  8359053  | `#7F8C8D` |
| `LightGrey`         | 12370112  | `#BCC0C0` |
| `Navy`              |  3426654  | `#34495E` |
| `DarkNavy`          |  2899536  | `#2C3E50` |
| `Yellow`            | 16776960  | `#FFFF00` |

### Cores Oficiais do Discord

| Name              | Int Color | Hex Code  |
|-------------------|:---------:|:---------:|
| `White` (Default) | 16777215  | `#FFFFFF` |
| `Greyple`         | 10070709  | `#99AAb5` |
| `Black`           |  2303786  | `#23272A` |
| `DarkButNotBlack` |  2895667  | `#2C2F33` |
| `NotQuiteBlack`   |  2303786  | `#23272A` |
| `Blurple`         |  5793266  | `#5865F2` |
| `Green`           |  5763719  | `#57F287` |
| `Yellow`          | 16705372  | `#FEE75C` |
| `Fuchsia`         | 15418782  | `#EB459E` |
| `Red`             | 15548997  | `#ED4245` |

### Retorno

O método `register` retorna um objeto JSON contendo informações detalhadas sobre o erro e o status da mensagem enviada:

```json
{
    "status": 200,
    "data": {
        "filename": "...",
        "function": "...",
        "type_error": "...",
        "error": "...",
        "line": "...",
        "created_at": "...",
        "bot_name": "...",
        "default_user": "..."
    },
    "message": "Mensagem enviada com sucesso para o Discord"
}
```

### Parâmetros

- **webhook** (obrigatório): Um dicionário contendo o `id` e `token` do webhook do Discord.

```json
{"id": int, "token": str}
```
- **mongo** (Opcional): um dicionario contendo o `mongo_uri`, `db_name` e `collection_name` das conexões do mongo.
    - mongo_uri (str): A URI de conexão com o MongoDB. Exemplo: 'mongodb://localhost:27017'.
    - db_name (str): O nome do banco de dados onde os logs serão armazenados.
    - collection_name (str): O nome da collection onde os logs serão salvos.

```json

mongo_logger = {
        "mongo_uri":"mongodb://localhost:27017",
        "db_name":"logs_db",
        "collection_name":"logs"
    }

```    
Esses dados podem ser obtidos diretamente no Discord em: `https://discord.com/api/webhooks/<id>/<token>`.

- **default_user** (opcional): Nome do responsável pelo robô ou código.
- **bot_name** (opcional): Nome do robô ou aplicação que está rodando.
- **send_notification** (opcional): Define se a notificação será enviada ao Discord (padrão: `True`). Se definido como `False`, apenas registrará o erro sem enviar a mensagem.

## Exemplo de Mensagem no Discord

Quando um erro é registrado, a mensagem enviada para o canal do Discord incluirá detalhes como o tipo de erro, o nome do robô e o responsável:

```
[Erro] O robô Calculadora encontrou um problema:
Exception: divisão por zero
Responsável: Gelson Júnior
```

## Contribuindo

Contribuições são sempre bem-vindas! Se encontrar algum problema ou tiver sugestões de melhoria, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto é licenciado sob a licença MIT. Para mais informações, consulte o arquivo [LICENSE](LICENSE).

---

**Grupo Bachega**

