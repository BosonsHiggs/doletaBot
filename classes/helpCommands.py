from . import (
	discord, 
	app_commands,
	MenuButton,
	Decorators,
	typing,
	Utils
)

async def HelpCenter(client, **kwargs):
	@client.tree.command()
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def help(interaction: discord.Interaction):
		"""Ajuda com os comandos do bot"""
		guild_id = interaction.guild_id

		embed = discord.Embed(colour=discord.Colour(0xFF0074))
		embed.set_footer(text="By: BosonsHiggs Team ❤️")

		g = f""
		embeds = []
		cont =0
		embed = discord.Embed()

		help_t = []
		for i in range(1, 7):
			ccc=Utils().translator("help", str(Utils(client).contLan(guild_id, i)))
			help_t.append(ccc)
	
		tamHelp = len(help_t)

		for cont2, comando in enumerate(help_t):
			cont+=1
			
			g += f'**`{cont2+1}.`** {Utils().extract_startwith(comando)}\n```{comando.split(" -> ")[1]}```\n'

			if cont < 6:
				embed = discord.Embed(colour=Utils().random_discord_color(), description=g)

			if cont == 5 or cont2+1 == tamHelp: 
				embeds.append(embed)
				g = ''
				cont = 0
		try:
			view = MenuButton(embeds)
			await interaction.response.send_message(embed=embeds[0], view=view)
		except:
			pass
