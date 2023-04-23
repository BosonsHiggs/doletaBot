from . import (
	discord, 
	app_commands, 
	commands,
    partial,
    qrcode,
    ButtonLink,
    io,

)
async def setup_commands(client):
    #command 1
    @client.tree.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def delete_all_table(interaction: discord.Interaction):
        """
        Deletar a tabela de pagamentos!
        """
        client.MYSQL.delete_payments_table()

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
        order = await client.PAYPAL.create_paypal_order(amount)
        order_id = order["id"]

        try:
            client.MYSQL.create_payments_table()
            client.MYSQL.save_payment(interaction.user.id, order_id, amount)
        except Exception as e:
            print(e)

        approval_url = next(
            (link["href"] for link in order["links"] if link["rel"] == "approve"), None
        )

        if approval_url is None:
            await interaction.followup.send(content="Houve um erro ao processar a compra.")
            return

        content = f"O membro {interaction.user} (ID:`{interaction.user.id}`), comprou o produto de ordem `{order_id}` no valor de `R${amount}`! Caso o cliente tenha enfrentado algum erro envie o link abaixo para ele continuar comprando:\n{approval_url}"
        
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
        client.MYSQL.clear_payments_table()

        await interaction.followup.send(content=f'O banco de dados foi varrido com sucesso!', ephemeral=True)

    #command 4
    @client.tree.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(order_id="Ordem do pagamento")
    async def verify_order(interaction: discord.Interaction, order_id: str):
        """Verificar o estado de uma transação usando a ordem de pagamento"""
        payment_status = await client.PAYPAL.check_payment_status(order_id)

        await interaction.response.send_message(
            f'payment_status: {payment_status}', ephemeral=True
        )

    @client.tree.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(email="E-mail associado ao PayPal", amount="Dinheiro a ser transferido")
    async def transfer_money(interaction: discord.Interaction, email: str, amount: float):
        """Transferir dinheiro para uma conta PayPal usando E-mail"""
        result = await client.PAYPAL.transfer_money_to_email(email, amount)

        if result:
            await interaction.response.send_message(
                f'O pagamento de R${amount} foi enviado para a conta {email}!', ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'Ocorreu algom erro inesperado!', ephemeral=True
            )
