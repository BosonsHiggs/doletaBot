from . import (
	discord, 
	app_commands,
	Decorators,
	typing,
	Utils
)

async def CreatorCommands(client, **kwargs):
	MY_GUILD = kwargs.get("MY_GUILD")
	# command 1
	@client.tree.command()
	@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
	@Decorators().is_bot_owner
	@app_commands.guilds(MY_GUILD)
	async def get_table_command(interaction: discord.Interaction) -> None:
		"""gggg"""
		await interaction.response.defer(ephemeral=True, thinking=True)
		guild_id  = interaction.guild_id
		table_name = str(guild_id)
		tables = client.MYSQL.get_table_contents(table_name=str(table_name))

		for table in tables:
			print(table)
		
		#ccc=Utils().translator("set_language", str(Utils(client).contLan(guild_id, 1)))
		await interaction.followup.send(
			content=f'teste'
		)

	# command 2
	@client.tree.command()
	@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
	@Decorators().is_bot_owner
	@app_commands.guilds(MY_GUILD)
	async def sync_command_command(interaction: discord.Interaction, guilds: typing.Optional[str] = None, spec: typing.Optional[typing.Literal[
								"Clear and local sync",
								"Clear local slash",
								"Clear local message context",
								"Clear local user context",
								"Clear global slash",
								"Clear global message context",
								"Clear global user context",
								"Global sync",
								"Copy global to local",
								"Local sync"
								]
						] = None
	) -> None:
		"""ffff"""
		assert interaction.guild is not None

		##Guilds
		try:
			next_word = guilds.split(';', maxsplit=1)[-1].split(maxsplit=1)[0]
			next_word = next_word.replace(" ", "")

			if (next_word != guilds) and ( ';' not in guilds):
				ccc=Utils().translator("semicolon", str(Utils().contLan(interaction.guild_id, 1)))
				await interaction.response.send_message(content=f'> *{ccc}* 😪')
				return

			guilds = guilds.replace(" ", "").split(';')

			guilds = (discord.Object(id) for id in guilds)
		except:
			guilds = None
		#End guilds


		if guilds is None:
			guilds = interaction.guild
			if spec is not None:
				if spec.lower() == "clear and local sync":
					client.tree.clear_commands(guild=guilds)
					await client.tree.sync(guild=guilds)
				elif spec.lower() == "local sync":
					await client.tree.sync(guild=guilds)
				elif spec.lower() == "copy global to local":
					client.tree.copy_global_to(guild=guilds)
					await client.tree.sync(guild=guilds)
				elif spec.lower() == "clear local slash":
					client.tree.clear_commands(guild=guilds, type=discord.AppCommandType.chat_input)
					await client.tree.sync(guild=guilds)
				elif spec.lower() == "clear local message context":
					client.tree.clear_commands(guild=guilds, type=discord.AppCommandType.message)
					await client.tree.sync(guild=guilds)
				elif spec.lower() == "clear local user context":
					client.tree.clear_commands(guild=guilds, type=discord.AppCommandType.user)
					await client.tree.sync(guild=guilds)
				elif spec.lower() == "clear global slash":
					client.tree.clear_commands(guild=None, type=discord.AppCommandType.chat_input)
					await client.tree.sync()
				elif spec.lower() == "clear global message context":
					client.tree.clear_commands(guild=None, type=discord.AppCommandType.message)
					await client.tree.sync()
				elif spec.lower() == "clear global user context":
					client.tree.clear_commands(guild=None, type=discord.AppCommandType.user)
					await client.tree.sync()
				elif spec.lower() == "global sync":
					await client.tree.sync()
				return
				
			await interaction.response.send_message(
				content=f"Synced command(s) {'globally' if spec is None else 'to the current guild.'}"
			)
			

		fmt = 0
		for guild in guilds:
			try:
				await client.tree.sync(guild=guild)
			except discord.HTTPException:
				pass
			else:
				fmt += 1

		await interaction.response.edit_message(content=f"Synced the tree to guild{'s'[:fmt^1]}.")	