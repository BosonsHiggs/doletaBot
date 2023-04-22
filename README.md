# Discord Bot - Doleta Payments

This is a simple Discord bot that uses the PayPal API to process payments and manage roles. It allows administrators to create payments, check payment status, and automatically update roles based on successful payments.

# Features
1. Create a PayPal order for a user.
2. Generate a QR code with the approval link for the user to scan.
3. Check the payment status of an order.
4. Automatically update the user's role based on successful payments.
5. Handles errors and exceptions gracefully.

# Requirements
- Python 3.8+
- Discord.py 2.0+
- aiohttp 3.8+
- pymysql 1.0.2+
- qrcode 7.3+
- A Discord bot token
- A PayPal account with API credentials (Client ID and Secret)
- A MySQL database

# Instalation
I. Clone the repository:
```bash
git git@github.com:BosonsHiggs/doletaBot.git
```

III. Configure as variáveis de ambiente necessárias:
- DISCORD_BOT_TOKEN: O token do seu bot no Discord.
- PAGHIPER_API_KEY: Sua chave de API da PagHiper.
- PAGHIPER_TOKEN: Seu token da PagHiper.
- REDIS_URL: A URL de conexão com seu servidor Redis (exemplo: redis://localhost:6379).
- REDIS_PASSWORD: A senha do seu servidor Redis, se aplicável.

On Linux or MacOS:
```bash
export DISCORD_BOT_TOKEN='your_discord_bot_token'
export PAYPAL_BOT_ID='your_paypal_client_id'
export PAYPAL_BOT_SECRET='your_paypal_secret'
export MYSQL_USER='your_mysql_user'
export MYSQL_PASSWORD='your_mysql_password'
export MYSQL_DATABASE='your_database_name'

On Windows:
```bash
set DISCORD_BOT_TOKEN='your_discord_bot_token'
set PAYPAL_BOT_ID='your_paypal_client_id'
set PAYPAL_BOT_SECRET='your_paypal_secret'
set MYSQL_USER='your_mysql_user'
set MYSQL_PASSWORD='your_mysql_password'
set MYSQL_DATABASE='your_database_name'
```

# Installation and Configuration
To install and configure the Discord Doleta Bot, follow the steps below:

1. Clone the repository.
2. Install the necessary dependencies using pip install -r requirements.txt.
3. Create a .env file in the project root and add your PayPal and MySQL database credentials, along with the Discord bot token and any other necessary information.
4. Set up the MySQL database to store payments.
5. Start the bot by running python main.py.

# Setting up MySQL on Linux and Windows
## Linux: 

Update your package list:
```bash
sudo apt update
```
Install the MySQL server package:
```bash
sudo apt install mysql-server
```
Start the MySQL service:
```bash
sudo systemctl start mysql
```
Enable MySQL to start at boot:
```bash
sudo systemctl enable mysql
```
Run the MySQL secure installation script to secure your database server:
```bash
sudo mysql_secure_installation
```
Log in to MySQL as the root user:
```bash
sudo mysql -u root -p
```

## After logging in to MySQL, you can create a new database and user for your application:

Create a new database:
```sql
CREATE DATABASE mydb;
```
Create a new user and set a password for the user:
```sql
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
```
Grant all privileges for the new user on the new database:
```sql
GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'localhost';
```
Flush privileges to apply the changes:
```sql
FLUSH PRIVILEGES;
```
Exit MySQL:
```sql
EXIT;
```
Now you have MySQL set up on your Linux or Windows system, and you can use the new database and user for your application.

# Commands

To use the bot, you need to be an administrator of your Discord server. The bot provides the following commands:

- /payment <amount>: Create a PayPal order for the specified amount.
- /verify_order <order_id>: Check the payment status of an order.
- /delete_all_table: Delete the payments table from the database.

The bot will automatically update the user's role and send a message in the specified channel when a payment is successful.

# Notes
This bot uses the PayPal sandbox environment for testing. Replace the sandbox URLs with production URLs for real transactions.
Make sure the bot has the necessary permissions to manage roles in your Discord server.

# Disclaimer
This project is for educational purposes only. Use it at your own risk. The author is not responsible for any consequences resulting from the use of this bot.

# Contacts

- Autor: Aril Ogai and Vexy
- Contato do Discord: Aril Ogai#5646 and Vexy#1212
- E-mail de suporte: bosonshiggsteam@gmail.com

