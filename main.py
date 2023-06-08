import discord
import json
import time

client = discord.Client(intetnts=discord.Intents.all())


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    norml = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

server_path = 0
channel_path = 0
try:
    with open('config.json', 'r') as f:
        data = json.load(f)
except Exception:
    print(bcolors.WARNING, "Couldn't load in 'config.json'! \nPlease create one with following content:", bcolors.norml)
    print('{"tokens": []}')
    exit()
dashes = '---------------------------------------'


print(dashes)
print('Welcome!')
if data['tokens'] == []:
    print("Paste in your token, you don't have any saved.")
else:
    print('Choose a bot from the config or paste a new token here.')



for i, bot in enumerate(data['tokens']):
    bot_name = bot['name']
    print(f'{i + 1}. {bot_name}')


while True:
    response = input()

    try:
        response = int(response)
        try:
            token = data['tokens'][response - 1]['token']
            break
        except Exception:
            print('Could not find the token in the config!')
    except Exception:
        token = response
        break

@client.event
async def on_ready():
    print(dashes)
    if type(response) == str:
        save_or_no = input(f'Would you like to add the token to the config.json? [Y/N]')
        if save_or_no.lower() == 'y' or save_or_no.lower == 'yes':
            data['tokens'].append({
                "name": client.user.name,
                "token": token
            })
            with open('config.json', 'w') as f:
                json.dump(data, f)
            print('Added to config!')
        elif save_or_no.lower() == 'no' or save_or_no.lower() == 'n':
            print('Not added.')
        else:
            print(f"{save_or_no}, I'll take that as a no.")
        print(dashes)
    print(f"Logged in as {client.user}")
    print('Get started using the "ls", "cd" and "help" command!')

    while True:
        if not server_path and not channel_path:
            command = input('> ')
        elif server_path and not channel_path:
            command = input(f'{client.get_guild(server_path).name}> ')
        else:
            command = input(f'{client.get_guild(server_path).name}/{client.get_channel(channel_path).name}> ')
        if not command == '':
            short = command.split(" ", 1)[0]
            if short in operations:
                await operations[short](command)
            else:
                print(f"{command} is not a valid command!")
                print('Use "help" to view all commands.')




async def ls(cmd):
    if not server_path:
        for guild in client.guilds:
            print(f'{guild.name}({guild.id}) by {guild.owner} : {guild.member_count} Members')
        print('Use "cd" to select a server.')
    elif not channel_path:
        guild = client.get_guild(server_path)
        for channel in guild.text_channels:
            print(f'#{channel.name} : {channel.id}')
        print(dashes)
        print('Note: Only text channels are displayed')
        print('Use "cd" to select a chananel')
    else:
        channel = client.get_channel(channel_path)
        if not channel.permissions_for(channel.guild.get_member(client.user.id)).read_message_history:
            print("Bot doesn't have the permissions to read history!")
            return
        try:
            for msg in reversed(await channel.history(limit=50).flatten()):
                if msg.content == None:
                    print(f'<{msg.author}> [Embed, file or something]')
                else:
                    print(f'<{msg.author}> {msg.content}')
            print(dashes)
            print('Use send [message] to say something as the bot.')
        except discord.Forbidden:
            print("Bot doesn't have the permission to view this channel!")

async def cd(cmd: str):
    global server_path
    global channel_path

    cmd = cmd.removeprefix('cd ')
    cmd = cmd.replace('#', '')
    id = None
    try:
        id = int(cmd)
    except Exception:
        pass

    print(dashes)
    if cmd == '..' and not channel_path:
        server_path = 0
    elif cmd == '..' and channel_path:
        channel_path = 0
    elif cmd == '/':
        channel_path = 0
        server_path = 0
    elif not id == None and not server_path:
        if client.get_guild(id) != None:
            server_path = id
        else:
            print('Invalid guild ID!')
    elif not id == None and not channel_path:
        if client.get_guild(server_path).get_channel(id) != None:
            channel_path = id
            await ls(None)
        else:
            print('Invalid channel id!')
    elif id == None and not server_path:
        guilds_with_matching_name = []
        for guild in client.guilds:
            if guild.name == cmd:
                guilds_with_matching_name.append(guild)
        if guilds_with_matching_name == []:
            print("The bot is not in a guild named " + cmd + '!')
        elif len(guilds_with_matching_name) == 1:
            server_path = guilds_with_matching_name[0].id
        else:
            print('Multiple guilds with same name found! \nUse the "cd" command with the id.')
            for guild in guilds_with_matching_name:
                print(f'{guild.name}({guild.id}) by {guild.owner} : {guild.member_count} Members')
    elif id == None and not channel_path:
        channels = []
        for channel in client.get_guild(server_path).text_channels:
            if channel.name == cmd:
                channels.append(channel)
        if channels == []:
            print(f'Bot could not find channel {cmd}!')
        elif len(channels) == 1:
            channel_path = channels[0].id
            await ls(None)
        else:
            print('Multiple channels have been found! \nUse the "cd" command with the id.')
            for channel in channels:
                print(f'#{channel.name} : {channel.id}')
                await ls(None)
    else:
        print('You cannot go further than a channel.\nUse "cd .." or "cd /" to go back once or to server select')

async def send(cmd: str):
    cmd = cmd.removeprefix('send ')
    if channel_path == 0:
        print('You are not in a channel! \nUse the "ls" and "cd" commands to navigate to one!')
        return
    channel = client.get_channel(channel_path)
    try:
        await channel.send(cmd)
    except discord.Forbidden:
        print("Bot doesn't have permission to send here!")
    print('Done! Use "ls" to refresh the channel')


async def leave(cmd: str):
    cmd = cmd.removeprefix('leave ')
    try:
        cmd = int(cmd)
    except Exception:
        print(f'{cmd} is not a valid ID!')
    guild = client.get_guild(cmd)

    if guild == None:
        print('Guild not found!')
        return
    print(dashes)
    print(f'{guild.name}({guild.id}) by {guild.owner} : {guild.member_count} Members')
    print(dashes)
    while True:
        x = input('Leave this guild? [Y/N]')
        if x.lower() == 'y':
            try:
                await guild.leave()
            except Exception as ex:
                print('Could not leave guild :(\nError: ')
                time.sleep(2)
                print(ex)
            break
        elif x.lower() == 'n':
            print('Ok, nothing changed!')
            break
        else:
            print(f'Not sure what you mean by {x}.')

    
async def close(cmd):
    print('Bye :)')
    time.sleep(1)
    exit()

async def invite(cmd):
    print(dashes)
    if not channel_path:
        print('You have to be in a channel to create an invite.')
        return
    channel = client.get_channel(channel_path)
    if not channel.permissions_for(channel.guild.get_member(client.user.id)).create_instant_invite:
        print('Bot does not have permission to create invites in this channel!')
        return
    reason = input("Reason for invite (Leave blank for None) \n: ")
    if reason == '':
        reason = None
    invite = await channel.create_invite(reason=reason, max_age=None, max_uses=None)
    print(invite.url)

async def members(cmd):
    if not server_path:
        print('You have to be in a server directory to use this command!')
        return
    for member in client.get_guild(server_path).members:
        lvl = 'User'
        if member.guild_permissions.administrator:
            lvl = 'Admin'
        elif member.guild_permissions.kick_members or member.guild_permissions.manage_nicknames or member.guild_permissions.moderate_members:
            lvl = 'Mod'
        elif member.guild.owner.id == member.id:
            lvl = 'Owner'
        print(f'{member}({member.id}) : {lvl}')


async def open_dm(cmd: str):
    try:
        cmd = int(cmd.removeprefix('open_dm '))
    except Exception:
        cmd = 123 # Invalid ID :P
    user = await client.get_or_fetch_user(cmd)
    if user == None:
        print("Usage: open_dm [user_id], opens DM with a user")
        print("Have you checked if the id is valid?")
        return
    dm = user.dm_channel
    if dm == None:
        dm = await user.create_dm()
    history = reversed(await dm.history(limit=50).flatten())
    for msg in history:
        print(f'<{msg.author}> {msg.content}')
    print(dashes)
    while True:
        x = input('Enter text to send or type "r" to refresh the channel \nTo close the DM enter "exit" \n')
        if x == 'r':
            history = await dm.history(limit=50).flatten()
            for msg in reversed(history):
                print(f'<{msg.author}> {msg.content}')
            print(dashes)
        elif x == 'exit' or x == 'close' or x == 'exi':
            return
        else:
            await dm.send(x)
            print('Success!')
            print(dashes)

async def list_dms(cmd):
    for dm in client.private_channels:
        if isinstance(dm, discord.DMChannel):
            print(f'{dm.recipient} : {dm.recipient.id}')
    print(dashes)
    print('To open the DM chat with somebody use "open_dm [user_id]"')
    print('Also note that this list is empty after this program restarts!')



async def help(cmd):
    print("All avaible commands:")
    print("ls - Lists all servers or channels in a server")
    print("cd [item_name / id] - Chanages directory to a server or channel")
    print("channel [channel_id] - Changes directory to a channel id")
    print("leave [server_id] - Leaves a server")
    print("send [message] - Sends something in a channel or DM")
    print("invite - Creates an invite while in a channel directory")
    print("members - Lists all members from a guild directory")
    print("open_dm [user_id] - Opens DM chat with a user by his ID")
    print("list_dms - Lists out all DM chats with users")
    print("exit - Logs out of the bot and closes this program")




operations = {
    "help": help,
    "ls": ls,
    "cd": cd,
    "send": send,
    "leave": leave,
    "exit": close,
    "invite": invite,
    "members": members,
    "open_dm": open_dm,
    "list_dms": list_dms,
}
try:
    client.run(token)
except Exception:
    print('Invalid token! Program closing!')
    time.sleep(2)