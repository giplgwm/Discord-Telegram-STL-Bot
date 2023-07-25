from telethon import TelegramClient
from telethon import functions, types
from mega import Mega
import interactions
mega = Mega()
#FILL VALUES IN ALL CAPS IN WITH YOUR OWN INFO
#Discord API info
bot = interactions.Client(token="TOKEN")
#Telegram API info
api_id = API_ID
api_hash = API_HASH
#Mega API info
m = mega.login(EMAIL, PASS)

#Establish a TelegramClient with the given api info, establish a list of unwanted filetypes (in this case images, commonly shared alongside the STLs i want to scrape). Also creating 2 empty lists that are used in later logic.
client = TelegramClient('anon', api_id, api_hash)
blacklist = [".png", ".jpg", ".gif", ".jpeg"]
Documents = []
Messages = []

#Discord bot command syntax.
@bot.command(
    name="fetch",
    description="Fetches stls based on search query, generates a link to download chosen file",
    options= [ interactions.Option(
        name="search",
        description="your search query",
        type=interactions.OptionType.STRING,
        required=True
    )
    ]
)
#defining the /fetch command which will take in a string, use it to query telegram, discard any duplicates or unwanted filetypes - then display the results and allow the user to choose which should be downloaded.
async def fetch(ctx: interactions.CommandContext, search:str):
    await ctx.send(f"Searching {search}", ephemeral=True)
    await client.start()
    print("Searching: " +search)
    Documents.clear()
    Messages.clear()
    options = []
    async for message in client.iter_messages(entity=None, search=search,
                                              filter=types.InputMessagesFilterDocument):
        if message.document is None:
            continue
        if any(x in message.document.attributes[-1].file_name for x in blacklist):
            continue
        if message.document.id in Documents:
            print("Skipping copy")
            continue
        Documents.append(message.document.id)
        Messages.append(message)
        print(message.document.attributes[-1].file_name)
        newoption = interactions.SelectOption(label=message.document.attributes[-1].file_name,value=len(options))
        options.append(newoption)

    print(f"We saved {len(Documents)}")
    optionmenu = interactions.SelectMenu(
        options=options[:24],
        custom_id="search_results"
    )
    value = await ctx.send("Select a file", components=optionmenu, ephemeral=True)
#Once the user chooses which file they want, this function downloads the file and uploads it to mega for the user to download at their leisure.
@bot.event
async def on_component(ctx: interactions.ComponentContext):
    await ctx.send("Downloading file from telegram", ephemeral=True)
    file = await Messages[int(ctx.data.values[0])].download_media()
    await ctx.send("Uploading file to MEGA", ephemeral=True)
    upload_file = m.upload(file)
    link = m.get_upload_link(upload_file)
    print(link)
    await ctx.send(f"Download {Messages[int(ctx.data.values[0])].document.attributes[-1].file_name}: {link}", ephemeral=True)
#Starts the discord bot
bot.start()

#Improvements to make: Error handling, Mega storage management (dont hit the limit, remove old files, remove downloaded files, etc)
#Features to add: Non-mega hosting
