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
CHANNEL_LOGS_DOLETA = DISCORD_CREDENTIALS[4]

## PAYPAL CREDENTIALS
PAYPAL_CLIENT_ID = PAYPAL_CREDENTIALS[0]
PAYPAL_SECRET = PAYPAL_CREDENTIALS[1]
PAYPAL_API_BASE_URL = 'https://api-m.sandbox.paypal.com' #https://api-m.paypal.com
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
		#await self.load_extension("classes.commands")
		# This copies the global commands over to your guild.

		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)


	async def on_ready(self) -> None:
		for guild in self.guilds:
			table_name = str(guild.id)

			try:
				self.client.MYSQL.create_payments_table(table_name=table_name)
			except:
				pass

			try:
				check_payments_task = CheckPaymentsTask(self, str(guild.id), seconds=0, minutes=5) #5x60s = 5min
				check_payments_task.start()
			except:
				pass
		
		print(f'{self.user.name} has connected to Discord!')

	"""async def on_error(self, event_method: str, *args, **kwargs) -> None:
			pass"""
	
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

client.MYSQL = MYSQL
client.PAYPAL = PAYPAL
client.UTILS = UTILS
client.member_timezone = member_timezone

client.CHANNEL_SUPPORT = DISCORD_CREDENTIALS[1]
client.MY_GUILD_DOLETA = DISCORD_CREDENTIALS[2]
client.ROLE_NAME = DISCORD_CREDENTIALS[3]
client.CHANNEL_LOGS_DOLETA = DISCORD_CREDENTIALS[4]

#Add bot owner IDs
client.owners = [690999812480303175, 1050954155503656960] 

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
			channel = bosons_guild.get_channel(int(CHANNEL_LOGS_DOLETA))

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
						app_commands.errors.MissingRole,
						app_commands.errors.MissingAnyRole,
						app_commands.errors.BotMissingPermissions,
						app_commands.errors.CommandInvokeError,
						app_commands.errors.AppCommandError,
						app_commands.errors.TransformerError,
						app_commands.errors.TranslationError,
						app_commands.errors.CheckFailure,
						app_commands.errors.CommandAlreadyRegistered,
						app_commands.errors.CommandSignatureMismatch,
						app_commands.errors.CommandNotFound,
						app_commands.errors.CommandLimitReached,
						app_commands.errors.NoPrivateMessage,
						app_commands.errors.MissingApplicationID,
						app_commands.errors.CommandSyncFailure
					)

	list_translations = (1, 6, 2, 7)
	for index, cmd in enumerate(command):
		if index > 3: break
		if isinstance(error, cmd):
			ccc=Utils().translator("on_error", str(Utils(client).contLan(guild_id, list_translations[index])))
			await interaction.response.send_message(
				f'> *{ccc}* 😪'.format(author.id), 
				ephemeral=False
			)

	#perm_bot = [command[1], command[4]]
	#cont=0
	for key in Utils().genList(command):
		#cont+=1
		if isinstance(error, key):
			#await ctx.send(cont-1)
			await logwrite(error)
	
	if isinstance(error, app_commands.CommandOnCooldown):
		try:
			retryAfter = [math.floor(math.ceil(error.retry_after) / 360), math.floor(error.retry_after / 60), error.retry_after % 86400]
			year, days, hours, minutes, seconds = Utils().format_seconds_time(int(retryAfter[2]))
			ccc1=Utils().translator("on_error", str(Utils(client).contLan(guild_id, 9)))
			ccc2=Utils().translator("on_error", str(Utils(client).contLan(guild_id, 10)))

			tempo = ccc2.format(year, days, hours, minutes, seconds)
			await interaction.response.send_message(
				f'*{ccc1}* ⏰'.format("/", str(interaction.command.name), tempo),
				ephemeral=True
				)
		except Exception as e:
			print(e)

async def main():
	async with client:
		#Commands
		await setup_commands(client)
		await HelpCenter(client)
		await CreatorCommands(client, MY_GUILD=MY_GUILD) #creators only
		
		#Start client
		await client.start(DISCORD_DOLETA_TOKEN)

asyncio.run(main())