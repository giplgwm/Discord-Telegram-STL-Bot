from telethon import TelegramClient, functions, types
from mega import Mega
import interactions
import os

# Config
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
TOKEN = 'YOUR_DISCORD_TOKEN'
EMAIL = 'YOUR_EMAIL'
PASS = 'YOUR_PASSWORD'

# Initialize
mega = Mega()
bot = interactions.Client(token=TOKEN)
client = TelegramClient('anon', API_ID, API_HASH)
blacklist = [".png", ".jpg", ".gif", ".jpeg"]
Documents = []
Messages = []

m = mega.login(EMAIL, PASS)

def remove_old_files(m, limit=10):
    """Remove old files from Mega to avoid hitting the storage limit."""
    files = m.get_files()
    if len(files) > limit:
        for file_id in list(files.keys())[limit:]:
            m.delete(file_id)

@bot.command(
    name="fetch",
    description="Fetches stls based on search query, generates a link to download chosen file",
    options=[interactions.Option(
        name="search",
        description="your search query",
        type=interactions.OptionType.STRING,
        required=True
    )]
)
async def fetch(ctx: interactions.CommandContext, search: str):
    await ctx.send(f"Searching {search}", ephemeral=True)
    await client.start()
    Documents.clear()
    Messages.clear()
    options = []
    async for message in client.iter_messages(entity=None, search=search, filter=types.InputMessagesFilterDocument):
        if message.document is None or any(x in message.document.attributes[-1].file_name for x in blacklist) or message.document.id in Documents:
            continue
        Documents.append(message.document.id)
        Messages.append(message)
        newoption = interactions.SelectOption(label=message.document.attributes[-1].file_name, value=len(options))
        options.append(newoption)

    optionmenu = interactions.SelectMenu(options=options[:24], custom_id="search_results")
    await ctx.send("Select a file", components=optionmenu, ephemeral=True)

@bot.event
async def on_component(ctx: interactions.ComponentContext):
    await ctx.send("Downloading file from telegram", ephemeral=True)
    file = await Messages[int(ctx.data.values[0])].download_media()
    await ctx.send("Uploading file to MEGA", ephemeral=True)
    upload_file = m.upload(file)
    link = m.get_upload_link(upload_file)
    await ctx.send(f"Download {Messages[int(ctx.data.values[0])].document.attributes[-1].file_name}: {link}", ephemeral=True)
    os.remove(file)  # Remove the downloaded file
    remove_old_files(m)  # Remove old files from Mega

bot.start()
