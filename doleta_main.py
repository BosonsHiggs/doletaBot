"""
os: é uma biblioteca nativa do Python que fornece uma interface para interagir com o sistema operacional no qual o código está sendo executado. É útil para tarefas como criar, excluir e renomear arquivos, além de definir variáveis de ambiente e obter informações sobre o sistema.
aiohttp: é uma biblioteca de clientes HTTP assíncronos para Python. É utilizada para fazer requisições web em serviços externos e é otimizada para trabalhar em conjunto com outras bibliotecas assíncronas, como asyncio.
json: é uma biblioteca nativa do Python que permite a conversão de objetos Python em formato JSON e vice-versa. É utilizada para trabalhar com dados que são transmitidos ou armazenados em formato JSON, que é uma estrutura de dados comum em APIs web.
asyncio: é uma biblioteca que permite a escrita de código assíncrono em Python, o que é útil para operações de entrada e saída intensivas, como fazer requisições de rede ou ler e escrever em arquivos.
aioredis: é uma biblioteca que fornece uma interface assíncrona para trabalhar com bancos de dados Redis. Redis é um banco de dados em memória que pode ser usado para armazenar dados em cache, filas de mensagens e outras tarefas que exigem alta velocidade e baixa latência.
ClientError: é uma exceção definida na biblioteca aiohttp que é lançada quando ocorre um erro durante uma requisição HTTP. É útil para lidar com erros de rede e garantir que seu aplicativo continue funcionando mesmo quando ocorrem problemas de conexão.
https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f
"""


from classes import *

##DISCORD CREDENTIALS
DISCORD_DOLETA_TOKEN = DISCORD_CREDENTIALS[0]
CHANNEL_SUPPORT = DISCORD_CREDENTIALS[1]
MY_GUILD_DOLETA = DISCORD_CREDENTIALS[2]
ROLE_NAME = DISCORD_CREDENTIALS[3]

## PAYPAL CREDENTIALS
PAYPAL_CLIENT_ID = PAYPAL_CREDENTIALS[0]
PAYPAL_SECRET = PAYPAL_CREDENTIALS[1]
PAYPAL_API_BASE_URL = 'https://api-m.sandbox.paypal.com'
PAYPAL = PayPal(PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_API_BASE_URL)

# Your MySQL database credentials
MYSQL_HOST = MYSQL_CREDENTIALS[0]
MYSQL_USER = MYSQL_CREDENTIALS[1]
MYSQL_PASSWORD = MYSQL_CREDENTIALS[2]
MYSQL_DATABASE = MYSQL_CREDENTIALS[3]
MYSQL = MySQL(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)

## UTILS FUNCTIONS
UTILS = Utils()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

member_timezone = pytz.timezone('America/Sao_Paulo')

MY_GUILD = discord.Object(id=int(MY_GUILD_DOLETA))  # replace with your guild id

class MyClient(discord.Client):
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		# This copies the global commands over to your guild.
		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)


	async def on_ready(self) -> None:
		print(f'{self.user.name} has connected to Discord!')
		try:
			MYSQL.create_payments_table()
		except Exception as e:
			print(e)
		try:
			await check_payments.start(self)
		except Exception as e:
			print('f', e)

	async def on_error(self, event_method: str, *args, **kwargs) -> None:
			pass

	async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
		if (ctx is None) or ctx.guild is None: return
		if error is None: return

		#await ctx.defer(ephemeral=False)
		guild = ctx.guild
		guild_id = guild.id
		channel_error = ctx.channel
		author = ctx.author

		async def logwrite(error):
			try:
				bosons_guild = self.get_guild(MY_GUILD_DOLETA)
				g = f'**⚠️ ERROR ALERT!**\n\n'
				g += f'```\n'
				g += f'Channel error {channel_error.name}: {error}\n'
				g += f'Server ID: {guild.id} - {guild.name}\n'
				g += f'Channel ID: {channel_error.id} - {channel_error.name}\n'
				g += f'{author.name}#{author.discriminator} (ID: {author.id}): {ctx.message.content}\n'
				g += f'```'
				channel = bosons_guild.get_channel(self.log_channel_id)

				await channel.send(content=g)
			except:
				pass
			
			try:
				with open('log.txt', 'a', encoding='utf-8') as log:
					log.write('-'*50)
					log.write(f'\nError on channel {channel_error.name}: {error}\n')
					log.write(f'Server: {guild.id} - {guild.name}\n')
					log.write(f'Channel ID: {channel_error.id} - {channel_error.name}\n')
					log.write(f'{author.name}#{author.discriminator} (ID: {author.id}): "{ctx.message.content}"\n\n')
			except:
				pass

		command = (
					commands.MissingPermissions, 
					commands.BotMissingPermissions, 
					commands.BotMissingRole,
					commands.MissingAnyRole,
					commands.BotMissingAnyRole, 
					commands.CommandInvokeError,
					commands.ConversionError, 
					commands.PrivateMessageOnly, 
					commands.NoPrivateMessage, 
					commands.CheckFailure, 
					commands.CheckAnyFailure,
					commands.RoleNotFound, 
					commands.BadInviteArgument, 
					commands.EmojiNotFound,
					commands.BadBoolArgument, 
					commands.MissingRole,
					commands.CommandRegistrationError, 
					commands.MessageNotFound, 
					commands.MissingRequiredArgument, 
					commands.ArgumentParsingError,
					commands.BadArgument, 
					commands.BadUnionArgument,
					commands.errors.HybridCommandError,
					AttributeError
				)
			
		for key in command:
			#cont+=1
			if isinstance(error, key):
				await logwrite(error)

		if isinstance(error, command[0]):
			ccc=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 6)))
			await ctx.send(f'> *{ccc}* 😪')

		if isinstance(error, command[1]):
			ccc=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 3)))
			await ctx.send(f'> *{ccc}* 😪')
		elif isinstance(error, command[0]):
			ccc=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 2)))
			name = f'<@{author.id}>'
			await ctx.send(f'> *{ccc}* 😪'.format(name))

		if isinstance(error, command[5]):
			ccc=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 6)))
			await ctx.send(f'> {ccc} 😪')

		if isinstance(error, command[23]):
			ccc=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 6)))
			await ctx.send(f'> {ccc} 😪')

		for key in range(19, 22):
			if isinstance(error, command[key]):
				ccc=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 5)))
				await ctx.send(f'> {ccc} 😪')
		
		if isinstance(error, commands.CommandOnCooldown):
			try:
				await ctx.defer(ephemeral=True)
				retryAfter = [math.floor(math.ceil(error.retry_after) / 360), math.floor(error.retry_after / 60), error.retry_after % 86400]
				year, days, hours, minutes, seconds = UTILS.format_seconds_time(int(retryAfter[2]))
				ccc1=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 7)))
				ccc2=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 8)))

				tempo = ccc2.format(year, days, hours, minutes, seconds)
				await ctx.send(f'*{ccc1}* ⏰'.format("/", str(ctx.command), tempo))
			except:
				pass
			#print('Command "%s" is on a %.3f second cooldown' % (ctx.command, error.retry_after))

		if hasattr(error, 'original'):
			if hasattr(error.original, 'cooldown'):
				if isinstance(error.original.cooldown, app_commands.checks.Cooldown):
					try:
						await ctx.defer(ephemeral=True)
						retryAfter = [math.floor(math.ceil(error.original.retry_after) / 360), math.floor(error.original.retry_after / 60), error.original.retry_after % 86400]
						year, days, hours, minutes, seconds = format_seconds_time(int(retryAfter[2]))
						ccc1=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 7)))
						ccc2=UTILS.translator("on_command_error", str(UTILS.contLan(guild_id, 8)))

						tempo = ccc2.format(year, days, hours, minutes, seconds)
						await ctx.send(f'*{ccc1}* ⏰'.format("/", str(ctx.command), tempo))
					except:
						pass

intents = discord.Intents(
			bans=True,
			dm_messages =True,
			dm_reactions=True,
			dm_typing=True,
			emojis=True,
			emojis_and_stickers=True,
			guild_messages=True,
			guild_reactions=True,
			guild_typing=True,
			guilds=True,
			integrations=True,
			invites=True,
			members=True,
			messages=True,
			message_content=True,
			presences=False,
			reactions=True,
			typing=True,
			voice_states=True,
			webhooks=True
			)

client = MyClient(intents=intents)

#command 1
@client.tree.command()
@commands.cooldown(1, 120, commands.BucketType.user)
@commands.has_permissions(administrator=True)
@app_commands.guilds(MY_GUILD)
async def delete_all_table(interaction: discord.Interaction):
	"""
	Deletar a tabela de pagamentos!
	"""
	MYSQL.delete_payments_table()

	await interaction.response.send_message(
		f'A tabela foi deletada com sucesso!', ephemeral=True
	)

#command 2
@client.tree.command()
@commands.cooldown(1, 120, commands.BucketType.user)
@commands.has_permissions(administrator=True)
@app_commands.describe(amount="Valor da compra")
async def payment(interaction: discord.Interaction, amount: float):
	"""Cria um pagamento"""

	await interaction.response.defer()
	guild = interaction.guild
	order = await PAYPAL.create_paypal_order(amount)
	order_id = order["id"]

	try:
		MYSQL.create_payments_table()
		MYSQL.save_payment(interaction.user.id, order_id, amount)
	except Exception as e:
		print(e)

	approval_url = next(
		(link["href"] for link in order["links"] if link["rel"] == "approve"), None
	)

	if approval_url is None:
		await interaction.followup.send(content="Houve um erro ao processar a compra.")
		return

	content = f"O membro {interaction.user} (ID:`{interaction.user.id}`), comprou o produto de ordem `{order_id}` no valor de `R${amount}`! Caso o cliente tenha enfrentado algum erro envie o link abaixo para ele continuar comprando:\n{approval_url}"
	channel = guild.get_channel(int(CHANNEL_SUPPORT))
	await channel.send(content=content)

	# Cria o QR code na memória
	qr = qrcode.QRCode(version=1, box_size=10, border=5)
	qr.add_data(approval_url)
	qr.make(fit=True)
	img_buffer = io.BytesIO()
	img = qr.make_image(fill_color="black", back_color="white")
	img.save(img_buffer, format='PNG')
	img_buffer.seek(0)
	file = discord.File(img_buffer, filename="qrcode.png")

	#View
	view = ButtonLink(approval_url, "Clique aqui!")
	
	# Envia a imagem como um arquivo
	await interaction.followup.send(
		content=f'Você está comprando R${amount} e sua ordem é `{order_id}`!',
		file=file,
		view=view, 
		ephemeral=True
	)

# command 3
@client.tree.command()
@commands.cooldown(1, 120, commands.BucketType.user)
@commands.has_permissions(administrator=True)
async def clear_payments(interaction: discord.Interaction):
	"""Limpar a tabela de pagamentos pendentes"""
	MYSQL.clear_payments_table()

	await interaction.response.send_message(
		f'O banco de dados foi varrido com sucesso!', ephemeral=True
	)

#command 4
@client.tree.command()
@commands.cooldown(1, 120, commands.BucketType.user)
@commands.has_permissions(administrator=True)
@app_commands.describe(order_id="Ordem do pagamento")
async def verify_order(interaction: discord.Interaction, order_id: str):
	"""Verificar o estado de uma transação usando a ordem de pagamento"""
	payment_status = await PAYPAL.check_payment_status(order_id)

	await interaction.response.send_message(
		f'payment_status: {payment_status}', ephemeral=True
	)

@client.tree.command()
@commands.cooldown(1, 120, commands.BucketType.user)
@commands.has_permissions(administrator=True)
@app_commands.describe(email="E-mail associado ao PayPal", amount="Dinheiro a ser transferido")
async def transfer_money(interaction: discord.Interaction, email: str, amount: float):
	"""Transferir dinheiro para uma conta PayPal usando E-mail"""
	result = await PAYPAL.transfer_money_to_email(email, amount)

	if result:
		await interaction.response.send_message(
			f'O pagamento de R${amount} foi enviado para a conta {email}!', ephemeral=True
		)
	else:
		await interaction.response.send_message(
			f'Ocorreu algom erro inesperado!', ephemeral=True
		)

##Tasks
@tasks.loop(seconds=20)
async def check_payments(bot: discord.Client):
	connection = MYSQL.get_mysql_connection()
	pending_payments = MYSQL.get_pending_payments(connection)

	if pending_payments is None: return
	if len(pending_payments) == 0: return

	for payment in UTILS.genList(pending_payments):
		payment_id, user_id, order_id, amount, status, timestamp = payment
		print(payment_id, user_id, order_id, amount, status, timestamp)
		
		#Check if it's within 1 day
		start_time = timestamp.astimezone(member_timezone)
		current_time = discord.utils.utcnow().astimezone(member_timezone)
		diff_time = current_time - start_time
		
		if diff_time.days > 1: 
			MYSQL.update_payment_status(user_id, order_id, 'OLD', connection)
			MYSQL.delete_payment_by_order_id(order_id, connection)
			await asyncio.sleep(1)
			continue

		if status != "PENDING": continue
		# Check if the payment was successful		
		payment_successful = await PAYPAL.is_payment_successful(order_id)

		print(f"Sucesso? {payment_successful}")
		if payment_successful:
			# Give the user their role and send a message in the specified channel
			guild = bot.get_guild(int(MY_GUILD_DOLETA))

			member = guild.get_member(int(UTILS.extract_numbers(user_id))) or await bot.fetch_user(int(UTILS.extract_numbers(user_id)))
			
			channel = guild.get_channel(int(CHANNEL_SUPPORT))

			bot_member = guild.get_member(client.user.id)
			bot_role = bot_member.top_role

			if bot_role.position == 0:
				await channel.send("O bot não possui permissões para criar ou modificar cargos.")
				return
			
			# Verificar se o cargo já existe
			role = discord.utils.get(guild.roles, name=ROLE_NAME)
			if not role:
				role = await guild.create_role(name=ROLE_NAME)
			await role.edit(position=bot_role.position - 1)

			await member.add_roles(role)

			await channel.send(f'O pagamento de ordem: `{order_id}` do {member.mention} (Name: {member} e ID: {member.id}) de R${amount} foi recebido com sucesso! 🥳')

			# Update the payment status in the database
			MYSQL.delete_payment_by_order_id(order_id)
			try:
				MYSQL.update_payment_status(user_id, order_id, 'COMPLETED', connection)
			except Exception as e:
				print(e)
		await asyncio.sleep(2)
	
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
	if (interaction is None) or interaction.guild is None: return
	if error is None: return

	#await ctx.defer(ephemeral=False)

	guild = interaction.guild
	guild_id = interaction.guild_id
	channel_error = interaction.channel
	author = interaction.user

	async def logwrite(error):
		try:
			bosons_guild = client.get_guild(int(MY_GUILD_DOLETA))
			g = f'**⚠️ ERROR ALERT!**\n\n'
			g += f'```\n'
			g += f'Channel error {channel_error.name}: {error}\n'
			g += f'Server: {guild_id} - {guild.name}\n'
			g += f'{author.name}#{author.discriminator}\n'
			g += f'```'
			channel = bosons_guild.get_channel(int(CHANNEL_SUPPORT))

			await channel.send(content=g)
		except:
			pass
		
		try:
			with open('log.txt', 'a', encoding='utf-8') as log:
				log.write('-'*50)
				log.write(f'\nError on channel {channel_error.name}: {error}\n')
				log.write(f'Server: {guild_id} - {guild.name}\n')
				log.write(f'{author.name}#{author.discriminator}"\n\n')
		except:
			pass
	
	command = (
						app_commands.errors.MissingPermissions,
						app_commands.errors.CommandInvokeError,
						app_commands.errors.AppCommandError
					)

	#perm_bot = [command[1], command[4]]
	#cont=0
	for key in command:
		#cont+=1
		if isinstance(error, key):
			#await ctx.send(cont-1)
			await logwrite(error)

	if isinstance(error, command[0]):
		ccc=UTILS.translator("on_error", str(UTILS.contLan(guild_id, 1)))
		await interaction.response.send_message(f'> *{ccc}* 😪'.format(author.id), ephemeral=True)

client.run(DISCORD_DOLETA_TOKEN)