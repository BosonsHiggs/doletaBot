from . import (
	discord, 
	app_commands,
	Decorators
)

async def CreatorCenter(client, **kwargs):
	MY_GUILD = kwargs.get("MY_GUILD")

	#@client.tree.command()
	#@app_commands.checks.cooldown(1, 120.0, key=lambda i: (i.guild_id, i.user.id))
	#@Decorators().is_bot_owner
	#@app_commands.guilds(MY_GUILD)
	#async def delete_all_table(interaction: discord.Interaction):
	#	"""
	#	Deletar a tabela de pagamentos!
	#	"""
	#	guild_id = interaction.guild_id
	#	client.MYSQL.delete_payments_table(table_name=guild_id)
#
	#	await interaction.response.send_message(
	#		f'A tabela {guild_id} foi deletada com sucesso!', ephemeral=True
	#	)