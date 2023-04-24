import os
import qrcode
import io
import asyncio
import math
import pytz
import pymysql
import aiohttp
import json
import functools
import discord
import re
import uuid
import typing
import random

from datetime import timedelta, datetime

#from typing import Optional
from discord.ext import commands, tasks
from discord import app_commands
from discord.utils import MISSING

from classes.utils import (
    MenuButton,
    ButtonLink,
    Decorators,
    PayPal,
    MySQL,
    Utils
)
from classes.newtasks import CheckPaymentsTask
from functools import partial
from classes.all_commands import setup_commands
from classes.helpCommands import HelpCenter
from classes.creatorCommands import CreatorCenter

PAYPAL_CREDENTIALS = (os.getenv("PAYPAL_GENERALBOT_ID"), os.getenv("PAYPAL_GENERALBOT_SECRET"))
MYSQL_CREDENTIALS = ("localhost", os.getenv("MYSQL_USER"), os.getenv("MYQSL_PASSWORD"), os.getenv("MYSQL_DATABASE_NAME"))
DISCORD_CREDENTIALS = (os.getenv('DISCORD_DOLETA_TOKEN'), os.getenv("CHANNEL_DOLETA_SUPPORT"), os.getenv("MY_GUILD_DOLETA"), "DOLETA USER", os.getenv("CHANNEL_LOGS_DOLETA"), os.getenv("DOLETA_APPLICATION_ID"))

__all__ = [
    'MISSING',
    'CheckPaymentsTask',
    'CreatorCenter',
    'Decorators',
    'HelpCenter',
    'setup_commands',
    'partial',
    'ButtonLink',
    'MenuButton',
    'app_commands',
    'tasks',
    'commands',
    'os', 
    'qrcode', 
    'io', 
    'asyncio', 
    'math', 
    'pytz', 
    'pymysql', 
    'aiohttp', 
    'json', 
    'functools', 
    'discord', 
    're', 
    'timedelta', 
    'datetime',
    'PAYPAL_CREDENTIALS',
    'MYSQL_CREDENTIALS',
    'DISCORD_CREDENTIALS',
    'PayPal',
    'MySQL',
    'Utils',
    'uuid',
    'typing',
    'random'
    ]