from . import (
	discord, 
	app_commands, 
	commands,
	partial,
	qrcode,
	ButtonLink,
	io,
	Decorators,
	typing,
	Utils
)

async def setup_commands(client, **kwargs):
	# command 1
	@client.tree.command()
	@app_commands.checks.cooldown(1, 120.0, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(amount="Valor da compra")
	async def payment(interaction: discord.Interaction, amount: float):
		"""Cria um pagamento"""

		await interaction.response.defer(ephemeral=True, thinking=True)
		guild = interaction.guild
		order = await client.PAYPAL.create_paypal_order(amount)
		order_id = order["id"]

		try:
			client.MYSQL.create_payments_table(table_name=str(guild.id))
		except:
			pass

		try:
			client.MYSQL.save_payment(interaction.user.id, order_id, amount, table_name=str(guild.id))
		except:
			pass

		approval_url = next(
			(link["href"] for link in order["links"] if link["rel"] == "approve"), None
		)

		if approval_url is None:
			ccc=Utils().translator("payment", str(Utils(client).contLan(guild.id, 1)))
			await interaction.followup.send(content=f"{ccc}")
			return

		ccc=Utils().translator("payment", str(Utils(client).contLan(guild.id, 2)))
		content = f"{ccc}".format(interaction.user, interaction.user.id, order_id, amount, approval_url)
		
		from . import DISCORD_CREDENTIALS

		CHANNEL_SUPPORT = DISCORD_CREDENTIALS[1]
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
		ccc=Utils().translator("payment", str(Utils(client).contLan(guild.id, 3)))
		await interaction.followup.send(
			content=f'{ccc}'.format(amount, order_id),
			file=file,
			view=view
		)

	# command 2
	@client.tree.command()
	@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(order_id="Ordem do pagamento")
	async def verify_order(interaction: discord.Interaction, order_id: str):
		"""Verificar o estado de uma transação usando a ordem de pagamento"""
		await interaction.response.defer(ephemeral=True, thinking=True)
		guild_id = interaction.guild_id
		payment_status = await client.PAYPAL.check_payment_status(order_id)

		if payment_status:
			ccc=Utils().translator("payment", str(Utils(client).contLan(guild_id, 1)))
			await interaction.followup.send(
				content=f'{ccc} ✅'.format(order_id)
			)
		else:
			ccc=Utils().translator("payment", str(Utils(client).contLan(guild_id, 2)))
			await interaction.followup.send(
				content=f'{ccc} ❌'.format(order_id)
			)

	# command 3
	@client.tree.command()
	@app_commands.checks.cooldown(1, 10*60.0, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.checks.has_permissions(administrator=True)
	async def delete_all_table(interaction: discord.Interaction):
		"""Deletar a tabela de pagamentos!"""
		await interaction.response.defer(ephemeral=True, thinking=True)
		guild_id = interaction.guild_id
		client.MYSQL.delete_payments_table(table_name=str(guild_id))

		ccc=Utils().translator("delete_all_table", str(Utils(client).contLan(guild_id, 1)))
		await interaction.followup.send(
				content=f'{ccc}'.format(guild_id)
		)

	# command 4
	@client.tree.command()
	@app_commands.checks.cooldown(1, 5*60.0, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.checks.has_permissions(administrator=True)
	async def clear_payments(interaction: discord.Interaction):
		"""Limpar a tabela de pagamentos pendentes"""
		await interaction.response.defer(ephemeral=True, thinking=True)
		guild_id = interaction.guild_id
		client.MYSQL.clear_payments_table(table_name=str(guild_id))

		ccc=Utils().translator("clear_payments", str(Utils(client).contLan(guild_id, 1)))
		await interaction.followup.send(
			content=f'{ccc}'.format(guild_id)
		)

	# command 5
	@client.tree.command()
	@app_commands.checks.cooldown(1, 10*60.0, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(language = "Definir linguagem do bot")
	async def set_language(interaction: discord.Interaction, language: typing.Literal['Português', 'English']):
		"""Definir o idioma do bot"""
		await interaction.response.defer(ephemeral=True, thinking=True)
		if language == "Português": language_ = "pt-br"
		elif language == "English": language_ = "en-us"
		else: language_ = "pt-br"

		guild_id = interaction.guild_id
		table_name = 'lan' + str(guild_id)
		client.MYSQL.create_languages_table(table_name=table_name)
		client.MYSQL.save_language(guild_id, language_, table_name=table_name)

		ccc=Utils().translator("set_language", str(Utils(client).contLan(guild_id, 1)))
		await interaction.followup.send(
			content=f'{ccc}'.format(language)
		)