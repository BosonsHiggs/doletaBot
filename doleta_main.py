"""
os: é uma biblioteca nativa do Python que fornece uma interface para interagir com o sistema operacional no qual o código está sendo executado. É útil para tarefas como criar, excluir e renomear arquivos, além de definir variáveis de ambiente e obter informações sobre o sistema.
aiohttp: é uma biblioteca de clientes HTTP assíncronos para Python. É utilizada para fazer requisições web em serviços externos e é otimizada para trabalhar em conjunto com outras bibliotecas assíncronas, como asyncio.
json: é uma biblioteca nativa do Python que permite a conversão de objetos Python em formato JSON e vice-versa. É utilizada para trabalhar com dados que são transmitidos ou armazenados em formato JSON, que é uma estrutura de dados comum em APIs web.
asyncio: é uma biblioteca que permite a escrita de código assíncrono em Python, o que é útil para operações de entrada e saída intensivas, como fazer requisições de rede ou ler e escrever em arquivos.
aioredis: é uma biblioteca que fornece uma interface assíncrona para trabalhar com bancos de dados Redis. Redis é um banco de dados em memória que pode ser usado para armazenar dados em cache, filas de mensagens e outras tarefas que exigem alta velocidade e baixa latência.
ClientError: é uma exceção definida na biblioteca aiohttp que é lançada quando ocorre um erro durante uma requisição HTTP. É útil para lidar com erros de rede e garantir que seu aplicativo continue funcionando mesmo quando ocorrem problemas de conexão.
"""

from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

import os, aiohttp, json, asyncio, aioredis
from aiohttp import ClientError

from classes.utils import *

DISCORD_DOLETA_TOKEN = os.environ['DISCORD_DOLETA_TOKEN']

CHANNEL_SUPPORT = os.getenv("CHANNEL_DOLETA_SUPPORT")
MY_GUILD_DOLETA = os.getenv("MY_GUILD_DOLETA")

MY_GUILD = discord.Object(id=MY_GUILD_DOLETA)  # replace with your guild id


class MyClient(discord.Client):
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		# This copies the global commands over to your guild.
		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
	print(f'Logged in as {client.user} (ID: {client.user.id})')
	print('------')

@client.tree.command()
@commands.cooldown(1, 120, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@app_commands.describe(
	payer_name = "Seu nome completo",
	payer_email = "Seu E-mail", 
	payer_cpf = "Seu CPF",
	payer_phone = "Seu número do celular",
	value = "Valor da compra"
)
async def pay_pix(interaction: discord.Interaction, payer_name: str, payer_email: str, payer_cpf: str, payer_phone: str, value: float):
	"""Fazer pagamentos com PIX pela API PagHiper"""

	if value < 3.0:
		await interaction.response.send_message("O valor deve ser maior que zero.")
		return
	
	price_cents = int(value*100)
	items = [{
				"description":"Compra de produto",
				"quantity":"1", "item_id":"1",
				"price_cents":str(price_cents)
			}
	]
		
	try:
		async with aiohttp.ClientSession() as session:
			qrcode_base64, pix_url, qrcode_image_url = await create_pix_charge(session, payer_name, payer_email, payer_cpf, payer_phone, value, items)
			print(qrcode_base64, pix_url, qrcode_image_url)
			qr_code_image = qr_base64_to_image(qrcode_base64)
		await interaction.response.send_message(f'Link para pagamento: {pix_url}', file=qr_code_image)
	except ClientError as e:
		await interaction.response.send_message(f'Erro ao criar cobrança: {str(e)[:200]}')
	except Exception as e:
		await interaction.response.send_message(f'Ocorreu um erro inesperado: {str(e)[:200]}')

@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
	"""Says when a member joined."""
	# If no member is explicitly provided then we use the command user here
	member = member or interaction.user

	# The format_dt function formats the date time into a human readable representation in the official client
	await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
	# The format_dt function formats the date time into a human readable representation in the official client
	await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


# This context menu command only works on messages
@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
	# We're sending this response message with ephemeral=True, so only the command executor can see it
	await interaction.response.send_message(
		f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
	)

	# Handle report by sending it into a log channel
	log_channel = interaction.guild.get_channel(CHANNEL_SUPPORT)  # replace with your channel id

	embed = discord.Embed(title='Reported Message')
	if message.content:
		embed.description = message.content

	embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
	embed.timestamp = message.created_at

	url_view = discord.ui.View()
	url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

	await log_channel.send(embed=embed, view=url_view)


client.run(DISCORD_DOLETA_TOKEN)