from . import (
	discord,
    MISSING,
    asyncio,
    tasks,
    Utils
)

class CheckPaymentsTask(tasks.Loop):
    def __init__(self, client: discord.Client, guild_id, *args, **kwargs):
        self.client = client
        self.guild_id = guild_id
        self.kwargs = kwargs
        self.table_name = f"{guild_id}" or 'payments'

        super().__init__(self.check_payments, seconds=kwargs.get("seconds"), hours=0, minutes=kwargs.get("minutes"), time=MISSING, count=None, reconnect=True)


    async def check_payments(self):
        connection = self.client.MYSQL.get_mysql_connection() if self.kwargs.get("connection") is None else self.kwargs.get("connection")
        pending_payments = self.client.MYSQL.get_pending_payments(connection, table_name= self.table_name)

        if len(pending_payments) == 0: return

        for payment in pending_payments:
            payment_id, user_id, order_id, amount, status, timestamp = payment
            #print(payment_id, user_id, order_id, amount, status, timestamp)
            
            #Check if it's within 1 day
            start_time = timestamp.astimezone(self.client.member_timezone)
            current_time = discord.utils.utcnow().astimezone(self.client.member_timezone)
            diff_time = current_time - start_time
            
            if diff_time.days > 1: 
                #MYSQL.update_payment_status(user_id, order_id, 'OLD', connection, table_name=str(guild_id))
                self.client.MYSQL.delete_payment_by_order_id(order_id, table_name=self.table_name)
                await asyncio.sleep(1)
                continue

            if status != "PENDING": continue
            # Check if the payment was successful		
            payment_successful = await self.client.PAYPAL.is_payment_successful(order_id)

            if payment_successful:
                # Give the user their role and send a message in the specified channel
                guild = self.client.get_guild(int(self.client.MY_GUILD_DOLETA))

                member = guild.get_member(int(Utils().extract_numbers(user_id))) or await self.client.fetch_user(int(Utils().extract_numbers(user_id)))
                
                channel = guild.get_channel(int(self.client.CHANNEL_SUPPORT))

                bot_member = guild.get_member(self.client.user.id)
                bot_role = bot_member.top_role

                if bot_role.position == 0:
                    ccc=Utils().translator("check_payments", str(Utils(self.client).contLan(self.guild_id, 1)))
                    await channel.send(f"{ccc}")
                    return
                
                # Verificar se o cargo já existe
                role = discord.utils.get(guild.roles, name=self.client.ROLE_NAME)
                if not role:
                    role = await guild.create_role(name=self.client.ROLE_NAME)
                await role.edit(position=bot_role.position - 1)

                await member.add_roles(role)

                ccc=Utils().translator("check_payments", str(Utils(self.client).contLan(self.guild_id, 2)))
                await channel.send(f'{ccc} 🥳'.format(order_id, member.mention, member, member.id, amount))

                # Update the payment status in the database
                self.client.MYSQL.delete_payment_by_order_id(order_id, table_name=self.table_name)
                try:
                    self.client.MYSQL.update_payment_status(user_id, order_id, 'COMPLETED', table_name=self.table_name)
                except:
                    pass
            await asyncio.sleep(2)