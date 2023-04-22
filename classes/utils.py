from . import (
	discord, 
	functools, 
	aiohttp, 
	datetime, 
	timedelta, 
	pymysql,
	re,
	json
)

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
def handle_aiohttp_errors(func):
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
FUNCTIONS
"""
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

	@handle_aiohttp_errors
	async def get_paypal_access_token(self):
		async with aiohttp.ClientSession() as session:
			auth = aiohttp.BasicAuth(self.PAYPAL_CLIENT_ID, self.PAYPAL_SECRET)
			data = {'grant_type': 'client_credentials'}
			async with session.post(f'{self.PAYPAL_API_BASE_URL}/v1/oauth2/token', auth=auth, data=data) as resp:
				response = await resp.json()
				return response['access_token']

	@handle_aiohttp_errors
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
			
	@handle_aiohttp_errors
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

	@handle_aiohttp_errors
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
	@handle_aiohttp_errors
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

	@handle_aiohttp_errors
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

	def save_payment(self, user_id, order_id, amount, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = "INSERT INTO payments (user_id, order_id, amount) VALUES (%s, %s, %s)"
				cursor.execute(sql, (user_id, order_id, amount))
				connection.commit()
		except Exception as e:
			print(f"Error in save_payment: {e}")  # Log added
		finally:
			connection.close()


	def get_pending_payments(self, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		pending_payments = []
		try:
			with connection.cursor() as cursor:
				sql = "SELECT * FROM payments WHERE status = 'PENDING'"
				cursor.execute(sql)
				pending_payments = cursor.fetchall()
		except Exception as e:
			print(f"Error in get_pending_payments: {e}")  # Log added
		finally:
			connection.close()
		return pending_payments


	def update_payment_status(self, user_id, order_id, status, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = "UPDATE payments SET status = %s WHERE user_id = %s AND order_id = %s"
				cursor.execute(sql, (status, user_id, order_id))
				connection.commit()
		finally:
			connection.close()

	#Create payments table
	def create_payments_table(self, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				# Verifica se a tabela já existe
				cursor.execute("SHOW TABLES LIKE 'payments'")
				result = cursor.fetchone()
				if result:
					pass
				else:
					# Cria a tabela
					sql = """CREATE TABLE payments (
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
	def delete_payments_table(self, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = "DROP TABLE IF EXISTS payments"
				cursor.execute(sql)
				connection.commit()
		finally:
			connection.close()

	#delete by user_id
	def delete_payment_by_user_id(self, user_id, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = "DELETE FROM payments WHERE user_id = %s"
				cursor.execute(sql, (user_id,))
				connection.commit()
		finally:
			connection.close()

	#Delete by order_id
	def delete_payment_by_order_id(self, order_id, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = "DELETE FROM payments WHERE order_id = %s"
				cursor.execute(sql, (order_id,))
				connection.commit()
		finally:
			connection.close()

	#Clear all table
	def clear_payments_table(self, connection=None):
		connection = self.get_mysql_connection() if connection is None else connection
		try:
			with connection.cursor() as cursor:
				sql = "TRUNCATE TABLE payments"
				cursor.execute(sql)
				connection.commit()
		finally:
			connection.close()

"""
OTHER FUNCTIONS
"""
class Utils:
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