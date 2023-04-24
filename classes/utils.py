from . import (
	discord, 
	functools, 
	aiohttp, 
	datetime, 
	timedelta, 
	pymysql,
	re,
	json, 
	uuid,
	random
)

##Don't import this
class MenuUtilities():
	def __init__(self, current_embed:discord.Embed=None, embed_compare:discord.Embed=None):
		self.current_embed = current_embed
		self.embed_compare = embed_compare

	def indexList(self, myList):
		for n in range(len(myList)):
			yield n

	def simplifyEmbed(self, embed1, embed2):
		embed1 = embed1.description.replace(' ', '').replace('\n', '')
		embed2 = embed2.description.replace(' ', '').replace('\n', '')

		return embed1, embed2

	##avançar uma vez
	def forwardEmbed(self):
		for index in self.indexList(self.embed_compare):
			embed1, embed2 = self.simplifyEmbed(self.current_embed, self.embed_compare[index])
			if embed1 != embed2: continue
			elif embed1 == embed2 and index < len(self.embed_compare)-1: return index + 1
			elif embed1 == embed2 and index >= len(self.embed_compare)-1: return index

	##Voltar uma vez
	def backwardEmbed(self):
		for index in self.indexList(self.embed_compare):
			embed1, embed2 = self.simplifyEmbed(self.current_embed, self.embed_compare[index])
			if embed1 != embed2: continue
			elif embed1 == embed2 and index > 0: return index - 1
			elif embed1 == embed2 and index <= 0: return index

class MenuButton(discord.ui.View):
	"""
	⏮️ -> track_previous
	◀️ -> arrow_backward
	▶️ -> arrow_forward
	⏭️ -> track_next 
	⏹️ -> stop_button
	"""
	def __init__(self, embeds:tuple=None, *args):
		super().__init__(timeout=None)
		self.embeds = embeds
		self.args = args
	
	@discord.ui.button(emoji='⏮️', style=discord.ButtonStyle.green, custom_id="persistent_view:track_previous")
	async def track_previous(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.edit_message(content=None, embed=self.embeds[0])
	
	@discord.ui.button(emoji='◀️', style=discord.ButtonStyle.green, custom_id="persistent_view:arrow_backward")
	async def arrow_backward(self, interaction: discord.Interaction, button: discord.ui.Button):
		index = MenuUtilities(interaction.message.embeds[0], self.embeds).backwardEmbed()
		await interaction.response.edit_message(content=None, embed=self.embeds[index])

	@discord.ui.button(emoji='▶️', style=discord.ButtonStyle.green, custom_id="persistent_view:arrow_forward")
	async def arrow_forward(self, interaction: discord.Interaction, button: discord.ui.Button):
		index = MenuUtilities(interaction.message.embeds[0], self.embeds).forwardEmbed()
		await interaction.response.edit_message(content=None, embed=self.embeds[index])

	@discord.ui.button(emoji='⏭️', style=discord.ButtonStyle.green, custom_id="persistent_view:track_next")
	async def track_next(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.edit_message(content=None, embed=self.embeds[len(self.embeds)-1])

	@discord.ui.button(emoji='⏹️', style=discord.ButtonStyle.red, custom_id="persistent_view:stop_button")
	async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.message.delete()

class ButtonLink(discord.ui.View):
	def __init__(self, url: str, button_label: str):
		super().__init__()

		# Link buttons cannot be made with the decorator
		# Therefore we have to manually create one.
		# We add the quoted url to the button, and add the button to the view.
		self.add_item(discord.ui.Button(label=button_label, url=url))

"""
DECORATORS
"""
class Decorators:
	#
	def is_bot_owner(self, func):
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			interaction = args[0] if isinstance(args[0], discord.Interaction) else args[1]
			if interaction.user.id not in interaction.client.owners:
				await interaction.response.send_message("Somente o dono do bot pode executar este comando.")
				return False
			return await func(*args, **kwargs)
		return wrapper

	def handle_aiohttp_errors(self, func):
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			try:
				result = await func(*args, **kwargs)
				return result
			except aiohttp.ClientError as e:
				print(f"Aiohttp error occurred: {e}")
				return None
			except Exception as e:
				print(f"An unexpected error occurred: {e}")
				return None
		return wrapper


"""
PAYPAL
"""
class PayPal:
	#from . import PAYPAL_CREDENTIALS, MYSQL_CREDENTIALS
	#PAYPAL_CLIENT_ID = PAYPAL_CREDENTIALS[0]
	#PAYPAL_SECRET = PAYPAL_CREDENTIALS[1]
	#PAYPAL_API_BASE_URL = 'https://api-m.sandbox.paypal.com'
	# Your PayPal API credentials: https://developer.paypal.com/dashboard
	# Sandbox URL, change to https://api-m.paypal.com for production	
	def __init__(self, PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_API_BASE_URL):
		self.PAYPAL_CLIENT_ID = PAYPAL_CLIENT_ID
		self.PAYPAL_SECRET = PAYPAL_SECRET
		self.PAYPAL_API_BASE_URL = PAYPAL_API_BASE_URL

	@Decorators().handle_aiohttp_errors
	async def get_paypal_access_token(self):
		async with aiohttp.ClientSession() as session:
			auth = aiohttp.BasicAuth(self.PAYPAL_CLIENT_ID, self.PAYPAL_SECRET)
			data = {'grant_type': 'client_credentials'}
			async with session.post(f'{self.PAYPAL_API_BASE_URL}/v1/oauth2/token', auth=auth, data=data) as resp:
				response = await resp.json()
				return response['access_token']

	@Decorators().handle_aiohttp_errors
	async def check_payment_status(self, order_id):
		access_token = await self.get_paypal_access_token()
		headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}
		async with aiohttp.ClientSession() as session:
			async with session.get(f'{self.PAYPAL_API_BASE_URL}/v2/checkout/orders/{order_id}', headers=headers) as resp:
				response = await resp.json()
				return response['status'] == 'COMPLETED'
			
	@Decorators().handle_aiohttp_errors
	async def create_paypal_order(self, amount):
		access_token = await self.get_paypal_access_token()
		headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}
		data = {
			'intent': 'CAPTURE',
			'purchase_units': [
				{
					'amount': {
						'currency_code': 'BRL',
						'value': amount
					}
				}
			],
			'application_context': {
				'return_url': 'https://discord.gg/Y9yxHDNSHJ',
				'cancel_url': 'https://discord.gg/Y9yxHDNSHJ',
				'accepted_currencies': ['BRL', 'USD', 'EUR']
			}
		}
		async with aiohttp.ClientSession() as session:
			async with session.post(f'{self.PAYPAL_API_BASE_URL}/v2/checkout/orders', headers=headers, json=data) as resp:
				response = await resp.json()
				return response

	@Decorators().handle_aiohttp_errors
	async def get_paypal_order(self, order_id):
		access_token = await self.get_paypal_access_token()
		headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}
		async with aiohttp.ClientSession() as session:
			async with session.get(f'{self.PAYPAL_API_BASE_URL}/v2/checkout/orders/{order_id}', headers=headers) as resp:
				response = await resp.json()
				return response

	#capture payment by order_id
	@Decorators().handle_aiohttp_errors
	async def capture_order(self, order_id):
		url = f"https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture"
		headers = {
			"Content-Type": "application/json"
		}
		async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.PAYPAL_CLIENT_ID, self.PAYPAL_SECRET)) as session:
			async with session.post(url, headers=headers) as response:
				return await response.json()

	async def is_payment_successful(self, order_id):
		verify_response = await self.capture_order(order_id)
		if 'status' in verify_response and verify_response['status'] == 'COMPLETED':
			return True
		return False

	@Decorators().handle_aiohttp_errors
	async def get_pending_list_payments(self):
		access_token = await self.get_paypal_access_token()
		headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json',
			'Accept': 'application/json'  # Add this line
		}
		
		#end_time = discord.utils.utcnow().replace(microsecond=0).isoformat() + 'Z'
		#start_time = (discord.utils.utcnow() - timedelta(days=3)).replace(microsecond=0).isoformat() + 'Z'
		end_time = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
		start_time = (datetime.utcnow() - timedelta(days=7)).replace(microsecond=0).isoformat() + 'Z'

		params = {
			'start_time': start_time,
			'end_time': end_time,
			'status': 'PENDING',
			'page_size': 100
		}

		async with aiohttp.ClientSession() as session:
			async with session.get(f'{self.PAYPAL_API_BASE_URL}/v2/payments/transactions', headers=headers, params=params) as resp:
				response = await resp.json()
				print(response)
				return response['transaction_details'] if 'transaction_details' in response else None

	async def get_completed_buyers(self):
		# Get an access token
		access_token = await self.get_paypal_access_token()
		
		# Set the endpoint URL and headers
		url = f'{self.PAYPAL_API_BASE_URL}/v2/payments/transactions'
		headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}
		
		# Set the parameters to filter the transactions
		params = {
			'start_time': '2022-01-01T00:00:00Z',  # Replace with your desired start time
			'end_time': '2022-01-31T23:59:59Z',    # Replace with your desired end time
			'transaction_status': 'COMPLETED'        # Replace with your desired transaction status
		}
		
		async with aiohttp.ClientSession() as session:
			async with session.get(url, headers=headers, params=params) as resp:
				response = await resp.json()
				transactions = response['transactions']
				
				# Extract the buyer information from each transaction
				buyers = []
				for transaction in transactions:
					buyer = {
						'name': transaction['payer']['name']['given_name'] + ' ' + transaction['payer']['name']['surname'],
						'email': transaction['payer']['email_address'],
						'amount': transaction['amount']['value'],
						'currency': transaction['amount']['currency_code']
					}
					buyers.append(buyer)
					
				return buyers

	async def transfer_money_to_email(self, email, amount):
		headers = {
			"Authorization": f"Bearer {await self.get_paypal_access_token()}",
			"Content-Type": "application/json",
		}
		data = {
			"sender_batch_header": {
				"sender_batch_id": f"batch-{uuid.uuid4()}",
				"email_subject": "You have a payment",
			},
			"items": [
				{
					"recipient_type": "EMAIL",
					"amount": {"value": amount, "currency": "BRL"},
					"note": "Thank you.",
					"receiver": email,
					"sender_item_id": str(uuid.uuid4()),
				}
			],
		}
		async with aiohttp.ClientSession() as session:
			async with session.post(
				f"{self.PAYPAL_API_BASE_URL}/v1/payments/payouts",
				headers=headers,
				json=data,
				auth=aiohttp.BasicAuth(self.PAYPAL_CLIENT_ID, self.PAYPAL_SECRET),
			) as resp:
				if resp.status == 201:
					response = await resp.json()
					return response["batch_header"]["batch_status"] == "SUCCESS"
				else:
					print(f"Transfer failed: {resp.reason}")
					return False

""""
MYSQL
"""
class MySQL:
	def __init__(self, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE) -> None:
		self.MYSQL_HOST = MYSQL_HOST
		self.MYSQL_USER = MYSQL_USER
		self.MYSQL_PASSWORD = MYSQL_PASSWORD
		self.MYSQL_DATABASE = MYSQL_DATABASE

	def get_mysql_connection(self):
		return pymysql.connect(host=self.MYSQL_HOST,
							user=self.MYSQL_USER,
							password=self.MYSQL_PASSWORD,
							database=self.MYSQL_DATABASE)

	# Create languages table
	def create_languages_table(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'languages'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
				result = cursor.fetchone()
				if result:
					pass
				else:
					sql = f"""CREATE TABLE `{table_name}` (
								id INT(11) NOT NULL AUTO_INCREMENT,
								guild_id VARCHAR(255) NOT NULL,
								language VARCHAR(255) NOT NULL,
								PRIMARY KEY (id)
							)"""
					cursor.execute(sql)
					connection.commit()
		finally:
			connection.close()

	def save_language(self, guild_id, language, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'languages'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"UPDATE `{table_name}` SET language = %s WHERE guild_id = %s"
				cursor.execute(sql, (language, guild_id))
				connection.commit()
				if cursor.rowcount == 0:
					sql = f"INSERT INTO `{table_name}` (guild_id, language) VALUES (%s, %s)"
					cursor.execute(sql, (guild_id, language))
					connection.commit()
		finally:
			connection.close()
	
	def get_language(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'languages'
		guild_id = kwargs.get("guild_id")
		connection = self.get_mysql_connection() if connection is None else connection
		language = None

		try:
			with connection.cursor() as cursor:
				sql = f"SELECT language FROM `{table_name}` WHERE guild_id = %s"
				cursor.execute(sql, (guild_id,))
				result = cursor.fetchone()
				if result:
					language = result[0]
		finally:
			connection.close()
		return language

	def save_payment(self, user_id, order_id, amount, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"INSERT INTO `{table_name}` (user_id, order_id, amount) VALUES (%s, %s, %s)"
				cursor.execute(sql, (user_id, order_id, amount))
				connection.commit()
		finally:
			connection.close()


	def get_pending_payments(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		pending_payments = []
		try:
			with connection.cursor() as cursor:
				sql = f"SELECT * FROM `{table_name}` WHERE status = 'PENDING'"
				cursor.execute(sql)
				pending_payments = cursor.fetchall()
		except:
			pending_payments = []
		finally:
			connection.close()
		return pending_payments


	def update_payment_status(self, user_id, order_id, status, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"UPDATE `{table_name}` SET status = %s WHERE user_id = %s AND order_id = %s"
				cursor.execute(sql, (status, user_id, order_id))
				connection.commit()
		finally:
			connection.close()
	
	def get_table_contents(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name")
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				cursor.execute(f"SELECT * FROM `{table_name}`")
				contents = cursor.fetchall()
		finally:
			connection.close()
		return contents
	
	#Create payments table
	def create_payments_table(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				# Verifica se a tabela já existe
				cursor.execute(f"SHOW TABLES LIKE '`{table_name}`'")
				result = cursor.fetchone()
				if result:
					pass
				else:
					# Cria a tabela
					sql = f"""CREATE TABLE `{table_name}` (
								id INT(11) NOT NULL AUTO_INCREMENT,
								user_id VARCHAR(255) NOT NULL,
								order_id VARCHAR(255) NOT NULL,
								amount DECIMAL(10, 2) NOT NULL,
								status ENUM('PENDING', 'COMPLETED') DEFAULT 'PENDING',
								created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
								PRIMARY KEY (id)
							)"""

					cursor.execute(sql)
					connection.commit()
		finally:
			connection.close()

	#delete the table
	def delete_payments_table(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"DROP TABLE IF EXISTS `{table_name}`"
				cursor.execute(sql)
				connection.commit()
		finally:
			connection.close()

	#delete by user_id
	def delete_payment_by_user_id(self, user_id, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"DELETE FROM `{table_name}` WHERE user_id = %s"
				cursor.execute(sql, (user_id,))
				connection.commit()
		finally:
			connection.close()

	#Delete by order_id
	def delete_payment_by_order_id(self, order_id, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"DELETE FROM `{table_name}` WHERE order_id = %s"
				cursor.execute(sql, (order_id,))
				connection.commit()
		finally:
			connection.close()

	#Clear all table
	def clear_payments_table(self, connection=None, **kwargs):
		table_name = kwargs.get("table_name") or 'payments'
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = f"TRUNCATE TABLE `{table_name}`"
				cursor.execute(sql)
				connection.commit()
		finally:
			connection.close()

"""
OTHER FUNCTIONS
"""
class Utils:
	def __init__(self, client: discord.Client = None) -> None:
		self.client = client

	def random_discord_color(self):
		return discord.Colour(random.randint(0, 0xFFFFFF))
	
	def extract_startwith(self, text:str) -> str:
		parts = text.split(' -> ')
		if parts[0].startswith('/'):
			return parts[0]
			
	def extract_numbers(self, text):
		return re.sub('[^0-9]', '', text)

	def genList(self, myList):
		for n in myList:
			yield n

	def path_lan(self):
		all_jsons = {
			"1":"classes/universal.json"
		}

		return all_jsons

	def contLan(self, id, num, language:str=None):
		table_name = 'lan' + str(id)
		language = self.client.MYSQL.get_language(guild_id=str(id), table_name=table_name)
		if language is None: 
			language = "pt-br"

		if language == "pt-br":
			return 2*num - 1
		elif language == "en-us":
			return 2*num
		else:
			return 2*num

	def translator(self, item, subitem):
		paths = self.path_lan()
		for path in paths.items():
			try:
				with open(path[1], "r", encoding="utf-8") as f:
					data = json.load(f)
					for p in data[item]:
						return p.get(subitem)
			except:
				continue

	def format_seconds_time(self, time):
		hours, remainder = divmod(time, 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		year, days = divmod(days, 365)

		return year, days, hours, minutes, seconds

	def datatime_time(self, timeout__, timein__):
		duration = timeout__ - timein__

		hours, remainder = divmod(int(duration.total_seconds()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		year, days = divmod(days, 365)