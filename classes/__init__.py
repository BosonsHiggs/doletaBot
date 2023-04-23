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

from datetime import timedelta, datetime

#from typing import Optional
from discord.ext import commands, tasks
from discord import app_commands
from classes.utils import *
from functools import partial
from classes.all_commands import setup_commands

PAYPAL_CREDENTIALS = (os.getenv("PAYPAL_GENERALBOT_ID"), os.getenv("PAYPAL_GENERALBOT_SECRET"))
MYSQL_CREDENTIALS = ("localhost", os.getenv("MYSQL_USER"), os.getenv("MYQSL_PASSWORD"), os.getenv("MYSQL_DATABASE_NAME"))
DISCORD_CREDENTIALS = (os.getenv('DISCORD_DOLETA_TOKEN'), os.getenv("CHANNEL_DOLETA_SUPPORT"), os.getenv("MY_GUILD_DOLETA"), "DOLETA USER", os.getenv("CHANNEL_LOGS_DOLETA"), os.getenv("DOLETA_APPLICATION_ID"))

__all__ = [
    'setup_commands',
    'partial',
    'ButtonLink',
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
    'uuid'
    ]