# Bot de Pagamento PIX para Discord

Este projeto é um bot de pagamento para Discord que utiliza o sistema PIX com a API da PagHiper. O bot permite a geração de cobranças e fornece links e QR Codes para pagamentos. Além disso, verifica em tempo real se o pagamento foi realizado com sucesso.

# Pré-requisitos
- Python 3.7 ou superior
- Conta na PagHiper com acesso à API
- Servidor Redis
- Bibliotecas Python: discord.py>=2.2.0, aiohttp==3.8.1 e aioredis==2.1.0

# Instalação
I. Clone o repositório:
```bash
git clone https://github.com/yourusername/pix-payment-bot.git
cd pix-payment-bot
```

II. Crie um ambiente virtual e instale as dependências:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

III. Configure as variáveis de ambiente necessárias:
- DISCORD_BOT_TOKEN: O token do seu bot no Discord.
- PAGHIPER_API_KEY: Sua chave de API da PagHiper.
- PAGHIPER_TOKEN: Seu token da PagHiper.
- REDIS_URL: A URL de conexão com seu servidor Redis (exemplo: redis://localhost:6379).
- REDIS_PASSWORD: A senha do seu servidor Redis, se aplicável.

No Linux ou macOS, configure as variáveis no terminal:
```bash
export DISCORD_BOT_TOKEN='your_discord_bot_token'
export PAGHIPER_API_KEY='your_paghiper_api_key'
export PAGHIPER_TOKEN='your_paghiper_token'
export REDIS_URL='redis://localhost:6379'
export REDIS_PASSWORD='your_redis_password'
export CHANNEL_DOLETA_SUPPORT='your_channel_support_id'
export MY_GUILD_DOLETA='your_support_server_id'
```

No Windows, configure as variáveis no prompt de comando:
```bash
set DISCORD_BOT_TOKEN=your_discord_bot_token
set PAGHIPER_API_KEY=your_paghiper_api_key
set PAGHIPER_TOKEN=your_paghiper_token
set REDIS_URL=redis://localhost:6379
set REDIS_PASSWORD=your_redis_password
set CHANNEL_DOLETA_SUPPORT='your_channel_support_id'
set MY_GUILD_DOLETA='your_support_server_id'
```

# Uso

I. Execute o bot:
```bash
python bot.py
```

II. No Discord, use o comando /pagar (em slash commands) com os seguintes parâmetros:
```
/pagar pagar <nome_do_pagador> <email_do_pagador> <cpf_do_pagador> <telefone_do_pagador> <valor>
```

# Gerando credenciais para a PagHiper:

I. Veja os procedimentos na página https://ajuda.sigecloud.com.br/como-obter-a-apikey-e-o-token-da-paghiper/

# Licença

Este projeto está licenciado sob a Licença Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional (CC BY-NC-SA 4.0). Consulte o arquivo LICENSE para obter detalhes.

- Autor: Aril Ogai
- Contato do Discord: Aril Ogai#5646
- E-mail de suporte: bosonshiggsteam@gmail.com

