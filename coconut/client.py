import discord
import socket
import sys
import functools

from coconut.config import get_config
from coconut.database import db
from coconut.models.server import Server
from coconut.models.user import User
from coconut.schema import Schema, command
from coconut.validators.blizzard_id import BlizzardIDValidator, BlizzardID

client = discord.Client()
config = get_config()
command_prefix = config.DEFAULT_COMMAND_PREFIX


@client.event
async def on_ready():
    print('Logged in as: {} - {}'.format(client.user.name, client.user.id))
    for server in client.servers:
        if not db.session.query(Server).filter_by(id=server.id).count():
            print('  Registering {}'.format(server.id))
            Server.create(id=server.id)
        else:
            print('  Already registered {}'.format(server.id))
    print('------')


@client.event
async def on_message(message):
    # await do(message)
    if not message.content.startswith(command_prefix) or message.author.bot:
        return
    tokens = message.content.split(' ')
    function_name = 'process_' + tokens.pop(0).lstrip(command_prefix)
    try:
        func = getattr(sys.modules[__name__], function_name)
    except AttributeError:
        pass
    else:
        try:
            print(function_name, tokens)
            await func(client, message, tokens=tokens)
        except:
            raise
        # except Exception:
        #     print('Problem in handler {} - {}'.format(function_name, message.content))


register_schema = Schema([BlizzardIDValidator('blizz_id')])


@command(register_schema)
async def process_register(client, message, blizz_id):
    author = message.author
    user = db.session.query(User).filter_by(id=author.id).first()
    verb = None
    if user:
        user.update(blizz_id=repr(blizz_id))
        verb = 'updated'
    else:
        user = User.create(id=author.id, blizz_id=repr(blizz_id), sr=None)
        verb = 'set'
    resp = "{} I {} your blizzard ID to: {}".format(author.mention, verb, user.blizz_id)
    await client.send_message(message.channel, resp)


def stashed_blizz_id(message):
    author = message.author
    user = db.session.query(User).filter_by(id=author.id).first()
    if user and user.blizz_id:
        return user.blizz_id
    return None


default_schema = Schema([BlizzardIDValidator('blizz_id', default='')])


def fetch_user(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        message = args[1]
        user = None
        if isinstance(message, discord.Message):
            author = message.author
            user = db.session.query(User).filter_by(id=author.id).first()
        kwargs['user'] = user
        return await func(*args, **kwargs)
    return wrapper


@command(default_schema)
@fetch_user
async def process_ob(client, message, blizz_id, user):
    author = message.author
    if not blizz_id and user:
        blizz_id = BlizzardID(*user.blizz_id.split('-'))
    if not blizz_id:
        resp = "{} Please supply a blizzard ID to query".format(author.mention)
        await client.send_message(message.channel, resp)
        return
    url = 'https://www.overbuff.com/players/pc/{}'.format(repr(blizz_id))
    await client.send_message(message.channel, url)


@command(default_schema)
@fetch_user
async def process_sr(client, message, blizz_id, user):
    author = message.author
    if not blizz_id and user:
        blizz_id = BlizzardID(*user.blizz_id.split('-'))
    if not blizz_id:
        resp = "{} Please supply a blizzard ID to query".format(author.mention)
        await client.send_message(message.channel, resp)
        return
    await client.send_typing(message.channel)
    data = None
    sr = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((config.OASIS_HOSTNAME, config.OASIS_PORT))
        s.sendall('pc\n'.format(blizz_id).encode())
        s.sendall('{}\n'.format(blizz_id).encode())
        data = s.recv(4096).decode().strip()
        s.close()
        if data.isdigit():
            sr = int(data)
    except:
        await client.send_message(message.channel, 'Internal server error')
        return

    resp = None
    if data is None:
        resp = 'OASIS Server closed unexpectedly'.format(data)
    if sr is None and data:
        resp = 'Received unrecognizable SR: {}'.format(data)
    else:
        if user and user.blizz_id == blizz_id:
            user.update(sr=sr)
        resp = '{} The estimated SR from OASIS for {} is: {}'.format(author.mention, blizz_id, sr)
    await client.send_message(message.channel, resp)


@command(Schema())
@fetch_user
async def process_info(client, message, user):
    author = message.author
    resp = None
    if user:
        resp = '{}\n```Blizzard ID: {}\nOASIS Estimate: {}```'.format(author.mention, user.blizz_id, user.sr)
    else:
        resp = 'I don\'t have any information for {}'.format(user.mention)
    await client.send_message(message.channel, resp)
