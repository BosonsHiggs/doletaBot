from . import (
	discord,
    MISSING,
    asyncio
)

class CheckPaymentsTask(discord.ext.tasks.Loop):
    def __init__(self, bot: discord.Client, guild_id, *args, **kwargs):
        self.client = bot
        self.guild_id = guild_id

        super().__init__(self.check_payments, seconds=20, hours=0, minutes=0, time=MISSING, count=None, reconnect=True)


    async def check_payments(self):
        connection = self.client.MYSQL.get_mysql_connection()
        pending_payments = self.client.MYSQL.get_pending_payments(connection, table_name=str(self.guild_id))

        if pending_payments is None: return
        if len(pending_payments) == 0: return

        try:
            print(self.client.UTILS().genList(pending_payments))
        except Exception as e:
            print(e)

        for payment in self.client.UTILS.genList(pending_payments):
            payment_id, user_id, order_id, amount, status, timestamp = payment
            print(payment_id, user_id, order_id, amount, status, timestamp)
            
            #Check if it's within 1 day
            start_time = timestamp.astimezone(self.client.member_timezone)
            current_time = discord.utils.utcnow().astimezone(self.client.member_timezone)
            diff_time = current_time - start_time
            
            if diff_time.days > 1: 
                #MYSQL.update_payment_status(user_id, order_id, 'OLD', connection, table_name=str(guild_id))
                self.client.MYSQL.delete_payment_by_order_id(order_id, connection, table_name=str(self.guild_id))
                await asyncio.sleep(1)
                continue

            if status != "PENDING": continue
            # Check if the payment was successful		
            payment_successful = await self.client.PAYPAL.is_payment_successful(order_id)

            if payment_successful:
                # Give the user their role and send a message in the specified channel
                guild = self.client.get_guild(int(self.client.MY_GUILD_DOLETA))

                member = guild.get_member(int(self.client.UTILS.extract_numbers(user_id))) or await self.client.fetch_user(int(self.client.UTILS.extract_numbers(user_id)))
                
                channel = guild.get_channel(int(self.client.CHANNEL_SUPPORT))

                bot_member = guild.get_member(self.client.user.id)
                bot_role = bot_member.top_role

                if bot_role.position == 0:
                    await channel.send("O bot não possui permissões para criar ou modificar cargos.")
                    return
                
                # Verificar se o cargo já existe
                role = discord.utils.get(guild.roles, name=self.client.ROLE_NAME)
                if not role:
                    role = await guild.create_role(name=self.client.ROLE_NAME)
                await role.edit(position=bot_role.position - 1)

                await member.add_roles(role)

                await channel.send(f'O pagamento de ordem: `{order_id}` do {member.mention} (Name: {member} e ID: {member.id}) de R${amount} foi recebido com sucesso! 🥳')

                # Update the payment status in the database
                self.client.MYSQL.delete_payment_by_order_id(order_id, table_name=str(self.guild_id))
                try:
                    self.client.MYSQL.update_payment_status(user_id, order_id, 'COMPLETED', connection, table_name=str(self.guild_id))
                except:
                    pass
            await asyncio.sleep(2)
