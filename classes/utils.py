import discord
import os, aiohttp, json, asyncio, aioredis
from PIL import Image
from io import BytesIO
import base64

from aiohttp import ClientError

PAGHIPER_API_KEY = os.environ['PAGHIPER_API_KEY']
PAGHIPER_TOKEN = os.environ['PAGHIPER_TOKEN']

REDIS_URL = os.environ['REDIS_URL']
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

def qr_base64_to_image(qr_base64) -> discord.File:
    qr_data = base64.b64decode(qr_base64)
    qr_code = Image.open(BytesIO(qr_data))
    
    qr_img = qr_base64_to_image(qr_code)
    qr_img_buffer = BytesIO()
    qr_img.save(qr_img_buffer, format="PNG")
    qr_img_buffer.seek(0)

    # Enviar a imagem como um arquivo anexado
    qr_file = discord.File(qr_img_buffer, filename="qr_code.png")

    return qr_file

async def connect_to_redis(REDIS_URL, REDIS_PASSWORD):
    return await aioredis.create_redis_pool(REDIS_URL, password=REDIS_PASSWORD)

async def save_transaction_to_redis(transaction_id, payer_name, payer_email, payer_cpf, payer_phone, value):
    transaction_data = {
        "transaction_id": transaction_id,
        "payer_name": payer_name,
        "payer_email": payer_email,
        "payer_cpf": payer_cpf,
        "payer_phone": payer_phone,
        "value": value,
        "status": "pending",
    }

    redis = await connect_to_redis()

    # Salva a transação no Redis com uma chave baseada no transaction_id
    await redis.set(f"transaction:{transaction_id}", json.dumps(transaction_data))

    # Adiciona o transaction_id à lista de transações pendentes para processamento
    await redis.rpush("pending_transactions", transaction_id)

    redis.close()
    await redis.wait_closed()

async def create_pix_charge(session, payer_name, payer_email, payer_cpf, payer_phone, value, items):
    api_url = "https://pix.paghiper.com/invoice/create/"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {
        "apiKey": PAGHIPER_API_KEY,
        "order_id": "32330335",
        "payer_email": payer_email,
        "payer_name": payer_name,
        "payer_cpf_cnpj": payer_cpf,
        "payer_phone": payer_phone,
        "notification_url": "https://mysite.com/notify/paghiper/",
        "discount_cents": "0",
        "shipping_price_cents": value,
        "shipping_methods": "PAC",
        "fixed_description": True,
        "days_due_date": "5",
        "items": items,
    }
    async with session.post(api_url, headers=headers, data=json.dumps(data)) as response:
        if response.status != 200:
            raise aiohttp.ClientError(f"API response: {response.status} - {await response.text()}")
        result = await response.json()

    if "pix_create_request" not in result or "status" not in result["pix_create_request"] or result["pix_create_request"]["status"] != "success":
        raise ValueError(f"Erro ao criar cobrança: {result}")

    transaction_id = result["pix_create_request"]["transaction_id"]
    qrcode_base64 = result["pix_create_request"]["pix_code"]["qrcode_base64"]
    pix_url = result["pix_create_request"]["pix_code"]["pix_url"]
    qrcode_image_url = result["pix_create_request"]["pix_code"]["qrcode_image_url"]

    await save_transaction_to_redis(transaction_id, payer_name, payer_email, payer_cpf, payer_phone, value)

    return qrcode_base64, pix_url, qrcode_image_url


async def check_transaction_status(session, transaction_id):
    """
    TODO:
    Esta função recebe o transaction_id como parâmetro e consulta a API da PagHiper 
    para obter o status da transação. A função retorna o status da transação conforme 
    retornado pela API.
    """
    api_url = "https://pix.paghiper.com/invoice/status/"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {
        "apiKey": PAGHIPER_API_KEY,
        "token": PAGHIPER_TOKEN,
        "transaction_id": transaction_id,
    }
    async with session.post(api_url, headers=headers, data=json.dumps(data)) as response:
        if response.status != 200:
            raise aiohttp.ClientError(f"API response: {response.status} - {await response.text()}")
        result = await response.json()

    if "status_request" not in result or "status" not in result["status_request"] or result["status_request"]["status"] != "success":
        raise ValueError(f"Erro ao verificar status da transação: {result}")

    return result["status_request"]["transaction"]["status"]


async def process_transaction_queue():
    """
    TODO:
    Esta função processa continuamente a fila de transações pendentes, verificando o status de 
    cada transação e atualizando-o no Redis. Se uma transação foi paga com sucesso, você pode 
    adicionar ações adicionais, como enviar confirmação, entregar produtos ou serviços, etc. 
    Se a transação ainda não foi paga, ela será adicionada novamente à lista de transações pendentes 
    para verificação posterior. A função aguarda um intervalo de tempo antes de processar a próxima 
    transação na fila.
    """
    while True:
        redis = await connect_to_redis()

        # Busca o próximo transaction_id na lista de transações pendentes
        transaction_id = await redis.lpop("pending_transactions")

        if transaction_id:
            transaction_key = f"transaction:{transaction_id}"
            transaction_data = await redis.get(transaction_key)

            if transaction_data:
                transaction_data = json.loads(transaction_data)

                # Verifica o status da transação
                async with aiohttp.ClientSession() as session:
                    try:
                        status = await check_transaction_status(session, transaction_id)
                    except Exception as e:
                        print(f"Erro ao verificar o status da transação {transaction_id}: {e}")
                        status = "error"

                # Atualiza o status da transação no Redis
                transaction_data["status"] = status
                await redis.set(transaction_key, json.dumps(transaction_data))

                # Se o status da transação for "paid", realiza ações adicionais (por exemplo, enviar confirmação, entregar produto, etc.)
                if status == "paid":
                    print(f"Transação {transaction_id} paga com sucesso!")
                    # Adicione aqui as ações a serem realizadas após a confirmação do pagamento

            # Se o status não for "paid", adiciona o transaction_id novamente na lista de transações pendentes
            if status != "paid":
                await redis.rpush("pending_transactions", transaction_id)

        redis.close()
        await redis.wait_closed()

        # Aguarda um intervalo antes de processar a próxima transação
        await asyncio.sleep(30)


def is_admin(user: discord.Member):
    return any(role.name == "Admin" for role in user.roles)